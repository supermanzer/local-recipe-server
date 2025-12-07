<template>
    <v-menu
     v-model="menu"
     :close-on-content-click="false"
     location="bottom start"
    >
        <template #activator="{props}">
            <v-btn
             variant="outlined"
             v-bind="props"
            >
                Restore Recipes
            </v-btn>
        </template>
        <v-card
         title="Restore Recipes"
         subtitle="Upload JSON file"
         min-width="400"
        >
            <v-card-text>
                <v-alert 
                  v-if="alert" 
                  title="Restore Response"
                  :type="alertType"
                  :text="alertText"
                  />
                <v-form>
                    <v-file-input
                    v-model="file"
                     label="Backup File"
                     hint="Select file to restore recipes from"
                     persistent-hint
                     accept="application/json"
                    />
                    <v-switch
                      v-model="overwrite"
                      label="Overwrite Existing"
                      color="deep-purple"
                      
                    />
                </v-form>
            </v-card-text>
            <v-card-actions>
                <v-spacer/>
                <v-btn
                  color="grey"
                  variant="text"
                  text="Cancel"
                  @click="clearAndClose"
                />
                <v-btn
                    color="indigo-darken-3"
                    variant="text"
                    text="Restore"
                    :disabled="file == null"
                    @click="uploadAndRestore"
                />
            </v-card-actions>
        </v-card>
    </v-menu>

</template>

<script setup lang="ts">
const {triggerRestore} = recipeUtils();

const menu = ref(false);
const file = ref(null);
const overwrite = ref(false);
const error = ref('');
const message = ref('');

const alert = computed(() => {
    return error.value.length > 0 || message.value.length > 0;
});

const alertType = computed(() => {
    return error.value.length > 0 ? 'error' : 'success';
});

const alertText = computed(() => {
    return error.value.length > 0 ? error.value : message.value;
});


const clearAndClose = () => {
    file.value = null;
    menu.value = false;
};

const uploadAndRestore = async() => {
    if (file.value !== null) {
        console.log("Received file: ", file.value);
        const result = await triggerRestore(file.value, overwrite.value);
        if (result.error !== null) {
            error.value = result.error;
        } else if (result.message !== null) {
            message.value = result.message
        } else {
            console.log("Result from restore action: ", result);
        };
    }
};
</script>