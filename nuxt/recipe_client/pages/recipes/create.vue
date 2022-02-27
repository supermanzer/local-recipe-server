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
                 <v-divider class="my-4"></v-divider>
                <v-row>
                    <v-col>
                        <v-form>
                            <v-textarea
                            v-model="response"
                            >

                            </v-textarea>
                        </v-form>
                    </v-col>
                </v-row>
             </v-card-text>
             <v-card-actions class="ma-8" justify="center" align="center">
                   <v-btn color="grey" @click="$router.push('/recipes')">Cancel</v-btn>
                   <v-spacer></v-spacer>
                   <v-btn color="green" @click="createRecipe()">Create</v-btn>
             </v-card-actions>
         </v-card>
     </v-col>
 </v-row>
</template>
 
<script>
export default {
   name: 'CreateRecipe',
   data: () => ({
       files: [],
       response: '',
   }),
   methods: {
       onFileChange(e) {
           this.files = e;
       },
       removeFile(index) {
           this.files.splice(index, 1);
       },
       async createRecipe() {
              const response = await this.$http.$post('/recipes/', {
                files: this.files,
              });
              this.response = JSON.stringify(response)
         },
       
    }
}
</script>