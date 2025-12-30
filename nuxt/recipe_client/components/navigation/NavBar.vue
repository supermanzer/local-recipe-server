<template>
    <v-app-bar color="primary" elevation="2" class="px-6">
        <v-btn v-show="!mobile" icon="mdi-home" @click="navigateTo('/')"/>
        <v-btn v-show="mobile" icon="mdi-menu" @click="drawer = !drawer" />
        <v-app-bar-title>Local Recipes</v-app-bar-title>
        <v-spacer/>

        <template #append>
           <v-row v-show="!mobile" class="mx-4">
                <v-btn
                 prepend-icon="mdi-logout"
                 text="logout"
                 @click="logoutRedirect"
                />
               <recipes-backup-recipe-button class="mx-2" />
               <recipes-restore-recipes class="mx-2" />
           </v-row>
        </template>
    </v-app-bar>

    <v-navigation-drawer v-if="mobile" v-model="drawer">
        <v-list-item title>Local Recipes</v-list-item>
        <v-divider/>
        <v-list-item subtitle="Navigation"/>
        <v-list-item>
            <v-btn 
             prepend-icon="mdi-home"
             text="Recipes"
             variant="text"
             class="mb-4"
             block
             @click="navigateTo('/')"
            />
        </v-list-item>
        <v-divider/>
        <v-list-item subtitle="Actions"/>
        <v-list-item class="mb-4">
            <v-btn  block variant="text" prepend-icon="mdi-logout" @click="logoutRedirect">Logout</v-btn>
        </v-list-item>
        <v-list-item class="mb-4">
            <recipes-backup-recipe-button :block="true" class="mx-2" />
        </v-list-item>
        <v-list-item class="mb-4">
            <recipes-restore-recipes :block="true" class="mx-2" />
        </v-list-item>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useDisplay } from 'vuetify';
const {logout} = useAuth();

const logoutRedirect = () => {
    logout();
    navigateTo('/login')
}

const {mobile} = useDisplay();

const drawer = ref(false);

</script>