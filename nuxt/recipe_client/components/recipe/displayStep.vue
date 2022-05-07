<template>
  <v-card class="mx-auto d-block my-6" hidden>
      <v-toolbar color="grey lighten-2" dense>
          <v-toolbar-title>
              Step {{step.number}}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon>
              <v-icon>
                  mdi-close-circle-outline
              </v-icon>
          </v-btn>
      </v-toolbar>
      <v-divider vertical class="px-3"></v-divider>
      <article class="px-10">
          {{step.text}}
      </article>
  </v-card>
</template>

<script>
export default {
    props: {
        step: {
            type: Object,
            required: true
        }
    },
    data: () => ({
        display:true
    }) 
}
</script>
