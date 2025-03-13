<template>
  <v-form v-if="hasStep">
      <v-row justify="center">
          <v-col cols="12" sm="3">
              <v-text-field
                v-model="myStep.number"
                label="Step Number"
                type="number"
                @input="updateStep"
              ></v-text-field>
          </v-col>
          <v-col cols="12" sm="9">
              <v-textarea
                v-model="myStep.text"
                label="Step Text"
                auto-grow
                @input="updateStep"
              ></v-textarea>
          </v-col>
      </v-row>
  </v-form>
</template>

<script>
export default {
    props: {
        step: {
            type: Object,
            default: () => {},
        },
    },
    data: () => ({
        myStep: null,
    }),
    computed: {
        hasStep() {
            return this.myStep !== null;
        },
    },
    mounted() {
        this.myStep = this.step;
    },
    methods: {
        updateStep() {
            this.$emit('input', this.myStep);
        },
    },
}
</script>
