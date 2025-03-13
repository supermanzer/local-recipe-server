<template>
  <div class="nav-wrapper">
    <nav v-show="show">
      <v-app-bar elevate-on-scroll>
        <v-toolbar-title
          class="text-uppercase mx-10"
          v-text="title"
        ></v-toolbar-title>
        <v-spacer></v-spacer>
        <div class="hidden-md-and-down">
          <v-btn
            v-for="route in routes"
            :key="route.title"
            :link="true"
            :to="route.to"
            icon
          >
            <v-icon>{{ route.icon }}</v-icon>
          </v-btn>
        </div>
      </v-app-bar>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'NavHeader',
  data: () => ({
    title: 'Manzer Recipes',
    routes: [
      {
        icon: 'mdi-home',
        title: 'Home',
        to: { name: 'index' },
      },
    ],
    show: true,
  }),
}
</script>
