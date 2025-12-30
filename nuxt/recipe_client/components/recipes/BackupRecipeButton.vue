<template>
    <div>
        <v-tooltip location="left" text="Create recipes backup file">
            <template #activator="{props}">
                <v-btn
                    prepend-icon="mdi-content-save"
                    text="backup"
                    variant="text"
                    :block="block"
                    v-bind="props"
                    @click="createBackup"
                />
            </template>
        </v-tooltip>
        <v-dialog
         v-model="isActive"
         width="auto"
        >
            <v-card
                :prepend-icon="icon"
                :text="dialogText"
                :title="title"
            >
                <template #actions>
                    <v-btn 
                     v-if="canDownload"
                     class="ms-auto"
                     variant="outlined"
                     text="Download File"
                     @click="downloadLatestBackup"
                    />
                    <v-btn
                        class="ms-auto"
                        text="Close"
                        @click="isActive = false"
                    />
                </template>
            </v-card>

        </v-dialog>
    </div>
</template>

<script setup lang="ts">
    const {triggerBackup, downloadLatestBackup} = recipeUtils();
    const {block} = defineProps({
        block: {type: Boolean, required: false, default: false}
    })

    const isActive = ref(false);
    const dialogText = ref('');
    const icon = ref('');
    const title = ref('');
    const canDownload = ref(false);

    const createBackup = async() => {
        const result = await triggerBackup()
        if (result.error) {
            dialogText.value = result.error
            icon.value = 'mdi-alert-outline'
            title.value = "Error"

        } else {
            dialogText.value = result.message || ''
            icon.value = 'mdi-check-circle-outline'
            title.value = "Success"
            canDownload.value = true;
        }
        isActive.value = true
    }
</script>