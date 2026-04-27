<template>
  <div class="bg-gray-800 rounded-xl p-6">
    <textarea
      v-model="input"
      class="w-full bg-gray-900 text-white rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
      rows="4"
      placeholder="请详细描述您的项目需求，例如：创建一个基于 FastAPI 的用户管理系统..."
      :disabled="disabled"
      @keydown.ctrl.enter="submitFull"
      @keydown.meta.enter="submitFull"
    />
    <div class="flex items-center justify-between mt-4">
      <span class="text-xs text-gray-500">Ctrl+Enter 提交完整流程</span>
      <div class="flex gap-3">
        <button
          v-if="showReset"
          @click="$emit('reset')"
          class="px-4 py-2 text-gray-400 hover:text-white transition-colors"
        >
          🔄 重置
        </button>
        <button
          @click="$emit('prd-only', input)"
          :disabled="disabled || !input.trim()"
          class="px-5 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
        >
          <span v-if="prdLoading">⏳ 生成中...</span>
          <span v-else>📋 仅生成 PRD</span>
        </button>
        <button
          @click="$emit('submit', input)"
          :disabled="disabled || !input.trim()"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
        >
          <span v-if="!disabled">🚀 开始开发</span>
          <span v-else>⚡ 开发中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  disabled: boolean
  showReset?: boolean
  prdLoading?: boolean
}>()

const emit = defineEmits<{
  submit: [requirement: string]
  'prd-only': [requirement: string]
  reset: []
}>()

const input = ref('')

function submitFull() {
  if (!input.value.trim() || props.disabled) return
  emit('submit', input.value.trim())
}
</script>
