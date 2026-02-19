/**
 * Provides mechanisms for authenticating front-end users
 * 
 * @module useAuth - handles logic for retrieving, storing, and refreshing auth tokens from the server and making authenticated requests
 * 
 */

import type { Ref } from "vue";

interface LoginCredentials {
    username: string
    password: string
}

interface TokenResponse {
    access: string
    refresh: string
}

const TOKEN_KEY = 'tokens'

/**
 * Extracts user-friendly error message from various error types
 */
const getErrorMessage = (error: any): string => {
    // Handle $fetch error responses
    if (error?.data?.detail) return error.data.detail
    if (error?.data?.error) return error.data.error
    if (error?.data?.message) return error.data.message

    // Handle multiple field errors (common in form validation)
    if (error?.data && typeof error.data === 'object') {
        const messages = Object.values(error.data)
            .filter(msg => typeof msg === 'string' || Array.isArray(msg))
            .map(msg => Array.isArray(msg) ? msg[0] : msg)
            .join(', ')
        if (messages) return messages
    }

    // Handle HTTP status codes
    if (error?.status === 401) return 'Unauthorized. Please check your credentials.'
    if (error?.status === 403) return 'You do not have permission to access this resource.'
    if (error?.status === 404) return 'Resource not found.'
    if (error?.status === 400) return 'Invalid request. Please check your input.'
    if (error?.status === 500) return 'Server error. Please try again later.'
    if (error?.status >= 500) return 'Server error. Please try again later.'
    if (error?.status >= 400) return `Error: ${error.status}. Please try again.`

    // Handle network errors
    if (error?.message?.includes('fetch')) return 'Network error. Please check your connection.'

    // Default fallback
    return error?.message || 'An unexpected error occurred. Please try again.'
}

export const useAuth = () => {
    const config = useRuntimeConfig()
    const { $api } = useNuxtApp();
    let baseURL = config.public.baseURL
    if (!baseURL) {
        baseURL = "/api"
    }


    const accessToken: Ref<string | null> = useState('auth.accessToken', () => null)
    const refreshToken: Ref<string | null> = useState('auth.refreshToken', () => null)
    const isAuthenticated: Ref<boolean> = useState('auth.isAuthenticated', () => false)
    const error: Ref<string | null> = useState('auth.error', () => null)

    const initAuth = () => {
        if (import.meta.client) {
            const stored = localStorage.getItem(TOKEN_KEY)

            if (stored) {
                console.log("GOT STORED TOKENS: ", stored);
                const tokens = JSON.parse(stored)
                accessToken.value = tokens.access
                refreshToken.value = tokens.refresh
                isAuthenticated.value = true
            }
        }
    }

    const login = async (credentials: LoginCredentials) => {
        try {
            const data = await $api<TokenResponse>('/token/', {
                baseURL,
                method: "POST",
                body: credentials
            })
            console.log("LOGIN SUCCESSFUL! RETURNED: ", data);

            accessToken.value = data.access
            refreshToken.value = data.refresh
            isAuthenticated.value = true
            if (import.meta.client) {
                console.log("LOCAL STORAGE SET:  ", data);
                localStorage.setItem(TOKEN_KEY, JSON.stringify(data))
            }
            // Schedule proactive token refresh
            scheduleTokenRefresh()
            return { success: true }
        } catch (error) {
            console.log("LOGIN ERROR:  ", error);

            return { success: false, error }
        }
    }

    const logout = () => {
        accessToken.value = null
        refreshToken.value = null
        isAuthenticated.value = false

        if (import.meta.client) {
            localStorage.removeItem(TOKEN_KEY)
        }
    }

    const refreshAccessToken = async () => {
        console.log("ATTEMPTING TO REFRESH ACCESS TOKEN");

        if (!refreshToken.value) {
            console.log("NO REFRESH TOKEN FOUND! USER MUST LOGIN AGAGIN");
            return false
        }

        try {
            console.log("MAKING REQUEST FOR FRESH ACCESS TOKEN");
            // This endpoint _only_ returns the access token
            const { access } = await $api<TokenResponse>('/token/refresh/', {
                baseURL,
                method: 'POST',
                body: { refresh: refreshToken.value },
            })
            console.log("ACCESS TOKEN RETURNED FROM TOKEN REFRESH ENDPOINT:  ", access);

            accessToken.value = access
            const data = {
                access,
                refrehs: refreshToken.value
            }

            if (import.meta.client) {
                console.log("SETTING LOCAL STORAGE WITH TOKENS:  ", data);

                localStorage.setItem(TOKEN_KEY, JSON.stringify(data))
            }
            // Schedule the next proactive refresh
            scheduleTokenRefresh()
            return true
        } catch (error) {
            console.log("REFRESH ERROR:  ", error);
            logout()
            return false
        }
    }

    const getTokenExpirationTime = (): number | null => {
        if (!accessToken.value) return null

        try {
            // JWT tokens have exp claim as the 3rd part separated by dots
            const parts = accessToken.value.split('.')
            if (parts.length !== 3) return null

            const decoded = JSON.parse(atob(parts[1]))
            // exp is in seconds, convert to milliseconds
            return decoded.exp ? decoded.exp * 1000 : null
        } catch (error) {
            console.log("Error decoding token expiration:", error)
            return null
        }
    }

    let refreshTimeout: ReturnType<typeof setTimeout> | null = null

    const scheduleTokenRefresh = () => {
        // Clear any existing scheduled refresh
        if (refreshTimeout) {
            clearTimeout(refreshTimeout)
        }

        const expirationTime = getTokenExpirationTime()
        if (!expirationTime) {
            console.log("Could not determine token expiration time")
            return
        }

        const now = Date.now()
        const timeUntilExpiry = expirationTime - now
        const refreshBefore = 60000 // Refresh 1 minute before expiry

        if (timeUntilExpiry <= 0) {
            // Token already expired, refresh immediately
            console.log("Token already expired, refreshing immediately")
            refreshAccessToken()
            return
        }

        if (timeUntilExpiry > refreshBefore) {
            // Schedule refresh before expiration
            const delay = timeUntilExpiry - refreshBefore
            console.log(`Token will be refreshed in ${Math.round(delay / 1000)} seconds (before expiry)`)
            refreshTimeout = setTimeout(() => {
                console.log("Proactively refreshing token before expiration")
                refreshAccessToken()
            }, delay)
        }
    }

    const authHeader = () => {
        return { Authorization: `Bearer ${accessToken.value}` }
    }

    const makeAuthRequest = async <T>(url: string, method: "GET" | "POST" | "PUT" | "DELETE", body: object = {}): Promise<T> => {
        console.log("MAKING AUTH REQUEST");
        const requestFunc = async (url: string, method: "GET" | "POST" | "PUT" | "DELETE") => {
            const options: Record<string, unknown> = {
                baseURL,
                method,
                headers: authHeader(),
            }
            if ((method === "POST" || method === "PUT") && body) {
                options.body = body
            }
            return await $fetch<T>(url, options)
        }

        try {
            const response = await requestFunc(url, method)
            console.log("AUTH REQUEST RESPONSE: ", response);
            return response
        } catch (error: any) {
            console.log("AUTH REQUEST ERROR:  ", error);

            // Check if error is specifically a 401 Unauthorized
            // $fetch throws with status property in error response
            const isUnauthorized = error?.status === 401 || error?.response?.status === 401

            if (!isUnauthorized) {
                // Re-throw non-401 errors (400, 403, 404, 500, network errors, etc.)
                console.log("Non-401 error, re-throwing:", error?.status);
                throw error
            }

            console.log("ATTEMPTING TOKEN REFRESH");
            const refreshSucceeded = await refreshAccessToken()

            // If refresh failed, log out and re-throw the original error
            if (!refreshSucceeded) {
                console.log("Token refresh failed, user needs to login again");
                throw error
            }

            // Token was successfully refreshed, retry the original request
            console.log("Token refreshed successfully, retrying request");
            const response = await requestFunc(url, method);
            return response
        }
    }

    return {
        accessToken,
        refreshToken,
        isAuthenticated,
        initAuth,
        login,
        logout,
        refreshAccessToken,
        makeAuthRequest,
        getTokenExpirationTime,
        scheduleTokenRefresh,
        getErrorMessage
    }
}
