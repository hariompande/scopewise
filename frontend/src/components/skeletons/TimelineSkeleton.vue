<template>
  <div class="space-y-3">
    <div v-for="i in 3" :key="i" class="p-3 border border-gray-200 rounded-md animate-pulse">
      <div class="flex justify-between items-start mb-2">
        <div class="h-5 bg-gray-200 rounded w-32"></div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
      </div>
      <div class="h-3 bg-gray-200 rounded w-2/3"></div>
    </div>
  </div>
</template>
