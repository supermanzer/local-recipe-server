/**
 * Global auth error interceptor 
 * Intercepts all $fetch requests and handles 401 and 403 responses
 */

export default defineNuxtPlugin((nuxtApp) => {
    console.log("Adding Auth API refresh");

    const $api = $fetch.create({
        onResponse({ response }) {
            if (response.status === 401 || response.status === 403) {
                console.log("REDIRECTING CLIENT TO LOGIN");

                navigateTo('/login')
            }
        },
        onResponseError({ response }) {
            if (response.status === 401 || response.status === 403) {
                console.log("REDIRECTING CLIENT TO LOGIN");
                navigateTo('/login')
            }
        }
    })
    nuxtApp.provide('api', $api)
})