<template>
    <div>
        <v-list lines="three" item-props>
            <template v-for="(step, idx) in steps" :key="step.id">
                <v-list-subheader v-if="idx === 0 && !step.component" title="Steps"></v-list-subheader>
                <v-list-subheader v-if="isNewComponentGroup(idx)" :title="`For the ${step.component}`"></v-list-subheader>
                <v-list-item
                    :active="activeStepId === step.id"
                    @click="selectStep(step)"
                    class="cursor-pointer"
                >
                    <template v-slot:prepend>
                        <v-icon :icon="`numeric-${step.order}-circle`"></v-icon>
                    </template>
                    <v-list-item-title>Step {{ step.order }}</v-list-item-title>
                    <p class="text-pre-wrap">{{ step.step }}</p>
                </v-list-item>
                <v-divider v-if="idx < steps.length - 1" :inset="true"></v-divider>
            </template>
        </v-list>
    </div>
</template>

<script setup lang="js">
const { steps } = defineProps({
    steps: { type: Array, required: false, default: () => [] }
})

const emit = defineEmits(['step-selected'])

const activeStepId = ref(null)

// A subheader is shown whenever a step starts a new (non-empty) component group,
// i.e. its component differs from the immediately preceding step's.
const isNewComponentGroup = (idx) => {
    if (!steps[idx]?.component) return false
    return idx === 0 || steps[idx - 1].component !== steps[idx].component
}

const selectStep = (step) => {
    activeStepId.value = step.id
    emit('step-selected', step)
}
</script>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
</style>