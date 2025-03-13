<template>
 <v-form>
     <v-row v-if="hasIngredient" justify="center">
         <v-col cols="12" sm="3">
             <v-text-field
             v-model="myIngredient.quantity"
            label="Quantity"
            type="number"
            clearable
            @input="updateIngredient"
             ></v-text-field>
         </v-col>
         <v-col cols="12" sm="3">
             <v-text-field
                v-model="myIngredient.unit"
                label="Unit"
                clearable
                @input="updateIngredient"
             ></v-text-field>
         </v-col>
         <v-col cols="12" sm="6">
                <v-text-field
                    v-model="myIngredient.name"
                    label="Name"
                    clearable
                    @input="updateIngredient"
                ></v-text-field>
         </v-col>
     </v-row>
 </v-form>
</template>

<script>
export default {
    props: {
        ingredient:{
            type: Object,
            default: () => {},
        }
    },
    data: () => ({
        myIngredient: null,
    }),
    computed: {
        hasIngredient() {
            return this.myIngredient !== null;
        },
    },
    mounted() {
        this.myIngredient = this.ingredient;
    },
    methods: {
        updateIngredient() {
            this.$emit('input', this.myIngredient);
        },
    },
}
</script>
