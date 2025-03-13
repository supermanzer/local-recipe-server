<template>
  <v-textarea
    v-model="myValue"
    :label="myLabel"
    auto-grow
  ></v-textarea>
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
    data: () =>({
        myLabel: '',
        myValue: '',
    })
}
</script>

