<template>
    <v-list :items="formattedSteps" lines="three" item-props>
        
    </v-list>
</template>

<script setup lang="js" >
const {steps} = defineProps({
    steps: {type: Array, required: false, default: () => []}
})

const getIcon = (step) => {
    return `numeric-${step.order}-circle`
}

const formattedSteps = steps.flatMap((step, idx) => {
  console.log('Index ', idx)
  const stepObj = {
    // prependAvatar: getIcon(step),
    title: `Step ${step.order}`,
    subtitle: step.step // or whatever property you want for subtitle
  };
  // Add a divider after each step except the last one
  if (idx < steps.length - 1) {
    return [stepObj, { type: 'divider', inset: true }];
  }
  if (idx == 0) {
    console.log("First items");
    
    return [{type: 'subheader', title: "Steps"}, stepObj]
  }
  return [stepObj];
});
</script>