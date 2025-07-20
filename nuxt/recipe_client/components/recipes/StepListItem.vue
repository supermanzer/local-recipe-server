<template>
    <v-list-item v-show="showStep">
        <template v-slot="prepend">
            <v-icon :icon="icon"></v-icon>
        </template>
        
    </v-list-item>
</template>

<script setup lang="js">
const {step} = defineProps({
    step: {type: Object, required: false, default: () => {}}
})

const showStep = ref(true)

const icon = computed(() => `numeric-${step.order}-circle`)
</script>