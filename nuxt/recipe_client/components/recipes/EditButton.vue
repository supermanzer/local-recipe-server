<template>
    <v-tooltip text="Edit Recipe">
        <template #activator="{props}">
            <v-btn
              v-bind="props"
              icon="mdi-pencil-outline"
              color="amber-darken-2"
              :to="editUrl"
            />
        </template>
    </v-tooltip>
</template>

<script setup lang="js">
const route  = useRoute();


const editUrl = computed(() => {
    return `/recipes/${route.params.id}-edit`
})
</script>