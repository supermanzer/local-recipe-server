<template>
    <v-app-bar color="primary" elevation="2" class="px-6">
        <v-btn icon="mdi-home" @click="navigateTo('/')"></v-btn>
        <v-app-bar-title >Local Recipes</v-app-bar-title>
        <v-spacer/>

        <template #append>
           <recipes-backup-recipe-button class="mx-2" />
           <recipes-restore-recipes class="mx-2" />
        </template>
    </v-app-bar>
</template>

