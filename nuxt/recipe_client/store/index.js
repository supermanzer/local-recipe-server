export const state = () => ({
    recipes:[],
    loading: false,
    requestOptions: {params: {}},
})

export const mutations = {
    setRecipes(state, recipes) {
        state.recipes = recipes
    },
    startLoading(state) {
        state.loading = true
    },
    stopLoading(state) {
        state.loading = false
    },
    setOptions(state, params) {
        state.requestOptions.params = params
    }

}

export const actions = {
    async filterRecipes(commit, params) {
        // const reqOptions = {params}
        commit('startLoading')
        const qs = this.$qs.stringify(params, {indices: false})
        const response = await this.$axios.$get(`/recipes/${qs}`)
        const recipes = response.results   
        commit('setRecipes', recipes)
        commit('stopLoading')
    }
}