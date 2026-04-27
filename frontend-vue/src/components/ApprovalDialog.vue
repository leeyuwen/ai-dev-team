<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="onCancel"
    >
      <div class="bg-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col border border-gray-700">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <div class="flex items-center gap-3">
            <span class="text-2xl">📋</span>
            <h2 class="text-lg font-semibold text-white">请确认产品规格文档</h2>
          </div>
          <button
            class="text-gray-400 hover:text-white transition-colors text-xl"
            @click="onCancel"
          >
            ✕
          </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <p class="text-sm text-gray-400 mb-3">
            请仔细阅读产品经理生成的需求文档，您可以修改后再继续。
          </p>
          <textarea
            v-model="editedSpec"
            class="w-full h-96 bg-gray-900 text-gray-200 rounded-lg p-4 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700"
            placeholder="产品规格文档内容..."
          />
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-700">
          <button
            class="px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-colors text-sm"
            @click="onCancel"
          >
            取消
          </button>
          <button
            class="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition-colors text-sm"
            @click="onApprove"
          >
            确认并继续 →
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  spec: string
}>()

const emit = defineEmits<{
  (e: 'approve', spec: string): void
  (e: 'cancel'): void
}>()

const editedSpec = ref('')

watch(() => props.spec, (val) => {
  editedSpec.value = val
}, { immediate: true })

function onApprove() {
  emit('approve', editedSpec.value)
}

function onCancel() {
  emit('cancel')
}
</script>
