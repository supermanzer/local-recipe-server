<template>
    <v-list :items="steps">
        <RecipesStepListItem v-for="step in steps" :key="step.id" :step="step" />
    </v-list>
</template>

<script setup lang="js" >
const {steps} = defineProps({
    steps: {type: Array, required: false, default: () => []}
})
</script>