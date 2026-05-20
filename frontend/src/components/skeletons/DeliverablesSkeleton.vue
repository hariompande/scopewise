<template>
  <div class="space-y-2">
    <div v-for="i in 4" :key="i" class="flex items-start gap-2">
      <div class="w-2 h-2 bg-gray-300 rounded-full mt-1.5 animate-pulse"></div>
      <div class="h-4 bg-gray-200 rounded flex-1 animate-pulse"></div>
    </div>
  </div>
</template>
