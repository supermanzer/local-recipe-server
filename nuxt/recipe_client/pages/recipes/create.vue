<template>
 <v-row justify="center" align="center">
     <v-col cols="12" sm="12" md="8">
         <v-card class="mx-auto" light>
             <v-card-title>
                   <span class="headline">Create Recipe</span>
             </v-card-title>
             <v-card-text>
                 <span>Upload image(s) of the recipe to create.  Once complete click the "Create" button below.</span>
                 <v-form class="ma-4">
                     <v-file-input
                       ref="finput"
                       counter                     
                       label="Upload Image(s)"
                       prepend-icon="mdi-camera"
                       multiple
                       show-size
                       @change="onFileChange"
                     ></v-file-input>
                 </v-form>
                 <v-list>
                       <v-list-item v-for="(file, index) in files" :key="index">
                           <v-list-item-content>
                               <v-list-item-title>{{ file.name }}</v-list-item-title>
                               <v-list-item-subtitle>{{ file.size }}</v-list-item-subtitle>
                           </v-list-item-content>
                           <v-list-item-action>
                               <v-btn icon @click="removeFile(index)">
                                   <v-icon>mdi-close</v-icon>
                               </v-btn>
                           </v-list-item-action>
                       </v-list-item>
                 </v-list>
             </v-card-text>
             <v-card-actions class="pa-8" justify="center" align="center">
                 <v-row v-if="!hasResponse" class="d-flex justify-space-around" >
                     <v-btn color="cancel" @click="$router.push('/recipes')">Cancel</v-btn>
                   
                    <v-btn color="success" @click="createRecipe()">Create</v-btn>
                 </v-row>
             </v-card-actions>
         </v-card>
         <v-card v-if="hasResponse" light>
             <v-card-title>
                 <span class="headline">Recipe Created</span>
             </v-card-title>
             <v-card-text>
                 <span class="subtitle">Review/edit the text below before confirming this recipe</span>
                <v-divider class="my-4"></v-divider>
               <create-form
                            :recipe="response"
                            @update:recipe="updateRecipe"
                            @reset:recipe="resetForm"
                            @confirm:recipe="saveRecipe"
                       ></create-form>
             </v-card-text>

         </v-card>
     </v-col>
 </v-row>
</template>
 
<script>
export default {
   name: 'CreateRecipe',
   data: () => ({
       files: [],
       response: null,
   }),
   computed: {
      hasResponse() {
        return this.response !== null;
      } 
    },
   methods: {
       onFileChange(e) {
           this.files = e;
       },
       removeFile(index) {
           this.files.splice(index, 1);
       },
       createRecipe() {
            const formData = new FormData();
            this.files.forEach(file => {
                formData.append('files', file);
            });
            this.$axios.post('/recipes/',formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            ).then((result) => {
                this.response = result.data
            }).catch((err) => {
                /* eslint no-console: off */
                console.error(err)
            });
            
         },
       updateRecipe(recipe) {
           this.response = recipe
       },
       resetForm() {
           this.response = null;
           this.files  = [];
           this.$refs.finput.clearableCallback();
       },
       async saveRecipe() {
           await this.$http.$post('/recipes/confirm/', {
               recipe_json: this.response,
           });
           
           this.$router.push('/recipes');
           
       }
    },
}
</script>