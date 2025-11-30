<template>
    <v-combobox
      v-if="ingredients"
      v-model="state.ingrediengs"
      :items="ingredients"
      item-title="name"
      item-value="id"
      @update:model-value="selectIngredient"
      multiple
      label="Search Ingredients"
      variant="underlined"
      chips
      clearable
      prepend-icon="mdi-magnify"
      />
</template>

<script setup lang="js">
const {getIngredients} = recipeUtils();
const emits = defineEmits(['ingedientSelected'])

const state = reactive({
    ingrediengs: []
})
const {data: ingredients, error} = await useAsyncData('ingredients',() => getIngredients());

const selectIngredient = () => {
    const ingredient_ids = state.ingrediengs.map((o) => o.id);
    emits('ingedientSelected', ingredient_ids)
}

</script>