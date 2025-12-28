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

export const useAuth = () => {
    const config = useRuntimeConfig()
    let baseURL = config.public.baseURL
    if (!baseURL) {
        baseURL = "http://localhost:8585/api"
    }
    console.log("BASE URL: ", baseURL);

    const accessToken: Ref<string | null> = useState('auth.accessToken', () => null)
    const refreshToken: Ref<string | null> = useState('auth.refreshToken', () => null)
    const isAuthenticated: Ref<boolean> = useState('auth.isAuthenticated', () => false)

    const initAuth = () => {
        if (import.meta.client) {
            const stored = localStorage.getItem(TOKEN_KEY)
            console.log("GOT STORED TOKENS: ", stored);

            if (stored) {
                const tokens = JSON.parse(stored)
                accessToken.value = tokens.access
                refreshToken.value = tokens.refresh
                isAuthenticated.value = true
            }
        }
    }

    const login = async (credentials: LoginCredentials) => {
        try {
            const data = await $fetch<TokenResponse>('/token/', {
                baseURL,
                method: "POST",
                body: credentials
            })
            console.log("LOGIN SUCCESSFUL! RETURNED: ", data);

            accessToken.value = data.access
            refreshToken.value = data.refresh
            isAuthenticated.value = true
            if (import.meta.client) {
                console.log("LOCAL STORAGE SET");
                localStorage.setItem(TOKEN_KEY, JSON.stringify(data))
            }
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
        if (!refreshToken.value) return false

        try {
            const data = await $fetch<TokenResponse>('/token/refresh/', {
                baseURL,
                method: 'POST',
                body: { refresh: refreshToken.value },
            })
            accessToken.value = data.access
            refreshToken.value = data.refresh

            if (import.meta.client) {
                localStorage.setItem(TOKEN_KEY, JSON.stringify(data))
            }
            return true
        } catch (error) {
            console.log("REFRESH ERROR:  ", error);
            logout()
        }
    }

    return {
        accessToken,
        refreshToken,
        isAuthenticated,
        initAuth,
        login,
        logout,
        refreshAccessToken
    }
}