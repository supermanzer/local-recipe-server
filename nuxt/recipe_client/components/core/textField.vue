<template>
  <v-text-field
   v-model="myValue"
   :label="myLabel"
   clearable
   @input="updateValue"
  ></v-text-field>
</template>

<script>
export default {
    props: {
        label: {
            type: String,
            default: '',
        },
        value: {
            type: String,
            default: '',
        },   
    },
    data: () => ({
        myLabel: '',
        myValue: '',
    }),
    mounted() {
        this.myLabel = this.label;
        this.myValue = this.value;
    },
    methods: {
        updateValue() {
            this.$emit('input', this.myValue);
        },
    },
}
</script>

