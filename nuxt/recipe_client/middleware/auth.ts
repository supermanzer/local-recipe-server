export default defineNuxtRouteMiddleware((to, _from) => {
    const { isAuthenticated } = useAuth()

    if (!isAuthenticated.value && to.path !== '/login') {
        return navigateTo('/login')
    }
})