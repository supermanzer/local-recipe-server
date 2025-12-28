<template>
    <div class="login-container">
        <v-card class="ma-auto" elevation="4">
            <v-card-title>Login For Recipes</v-card-title>
            <v-card-text>
                <v-form @submit.prevent="handeLogin">
                    <v-text-field
                      v-model="username"
                      label="Username"
                      type="text"
                      class="ma-4"
                    />
                    <v-text-field
                      v-model="password"
                      label="Password"
                      type="password"
                      outlined
                      class="ma-4"
                    />
                    <v-alert v-if="error" type="error" class="mb-4">
                        {{ error }}
                    </v-alert>
                    <v-btn color="primary" block type="submit" :loading="loading">
                        Login
                    </v-btn>
                </v-form>
            </v-card-text>
            <v-card-actions>
                <span>Accounts are managed by the system administrator</span>
            </v-card-actions>
        </v-card>
    </div>
</template>

<script setup lang="ts">
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)
    const _router = useRouter()
    const { login } = useAuth()
    const handeLogin = async () => {
        console.log("You are trying to log in!");

        loading.value = true 
        error.value = ''

        const result = await login({username: username.value, password: password.value})
        
        if (result.success) {
            await navigateTo('/')
        } else {
            error.value = "Invalid credentials"
            loading.value = false
        }
    }
</script>