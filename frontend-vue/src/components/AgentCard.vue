<template>
  <div
    class="rounded-lg p-4 border transition-all duration-300"
    :class="[
      isActive ? 'border-blue-500 bg-blue-900/20' : isDone ? 'border-green-600 bg-gray-900/50' : 'border-gray-700 bg-gray-900/30'
    ]"
  >
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xl">{{ icon }}</span>
      <span class="font-medium text-white text-sm">{{ label }}</span>
      <span v-if="isActive" class="ml-auto">
        <span class="inline-block w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
      </span>
      <span v-else-if="isDone" class="ml-auto text-green-400">✓</span>
    </div>

    <div v-if="content" class="text-xs text-gray-300 leading-relaxed">
      <pre class="whitespace-pre-wrap break-words font-sans">{{ truncate(content, 200) }}</pre>
    </div>
    <div v-else-if="isActive" class="text-xs text-gray-500 italic">
      执行中...
    </div>
    <div v-else class="text-xs text-gray-600">
      等待中
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgentStep } from '../types'

defineProps<{
  agentKey: AgentStep
  label: string
  icon: string
  content: string
  isActive: boolean
  isDone: boolean
}>()

function truncate(text: string, maxLen: number): string {
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}
</script>
