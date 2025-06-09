<template>
    <v-list-item>
        {{ step }}
    </v-list-item>
</template>

<script setup lang="js">
const {step} = defineProps({
    step: {type: Object, required: false, default: () => {}}
})
</script>