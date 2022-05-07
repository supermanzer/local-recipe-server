<template>
  <v-list-item>
      <v-list-item-icon>
          <v-icon color="primary">
              mdi-circle-medium
          </v-icon>
      </v-list-item-icon>
      <v-list-item-content>
          <v-list-item-title>
            <span  v-if="hasText(ingredient.amount)" class="mx-1">
                {{ingredient.amount }}
            </span>              
            <span  v-if="hasText(ingredient.unit)" class="mx-1">
                {{ingredient.unit }}
            </span>              
            <span  v-if="hasText(ingredient.name)" class="mx-1">
                {{ingredient.name }}
            </span>              
        </v-list-item-title>
      </v-list-item-content>
  </v-list-item>
</template>

<script>
export default {
    name: 'IngredientDisplay',
    props: {
        ingredient: {
            type: Object,
            required: true
        }
    },
    methods: {
        hasText(string){
            return string.length > 0
        }
    }
}
</script>
