<template>
    <v-menu
     v-model="menu"
     :close-on-content-click="false"
     location="bottom start"
    >
        <template #activator="{props: menu2}">
            <v-tooltip location="left" text="Restore recipes from backup">
                <template #activator="{props: tooltip}">
                    <v-btn
                        variant="text"
                        v-bind="mergeProps(menu2, tooltip)"
                        :block="block"
                        prepend-icon="mdi-backup-restore"
                        text="Restore"
                    />
                </template>
            </v-tooltip>
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
                  class="mb-6"
                  closable
                  @click:close="dismiss"
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
import { mergeProps } from 'vue';

const {triggerRestore} = recipeUtils();
const {block} = defineProps({
        block: {type: Boolean, required: false, default: false}
})

const menu = ref(false);
const file = ref(null);
const overwrite = ref(false);
const restorError = ref('');
const restoreMessage = ref('');

const alert = computed(() => {
    return restorError.value.length > 0 || restoreMessage.value.length > 0;
});

const alertType = computed(() => {

    return restorError.value.length > 0 ? 'error' : 'success';
});

const alertText = computed(() => {
    return restorError.value.length > 0 ? restorError.value : restoreMessage.value;
});


const clearAndClose = () => {
    file.value = null;
    menu.value = false;
};

const uploadAndRestore = async() => {
    if (file.value !== null) {
        console.log("Received file: ", file.value);
        const {error, message, status} = await triggerRestore(file.value, overwrite.value);
        if (error) {
            restorError.value = error;
        } else if (message) {
            restoreMessage.value = message
        } else {
            console.log("Result from restore action: ", status);
        };
    }
};

const dismiss = () => {
    restorError.value = '';
    restoreMessage.value = '';
    file.value = null;
    menu.value = false;
}
</script>