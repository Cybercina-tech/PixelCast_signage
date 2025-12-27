# Delete Confirmation Dialog - Usage Guide

## Overview

The Delete Confirmation Dialog is a reusable, accessible, and theme-aware component that replaces native JavaScript `confirm()` dialogs throughout the application.

## Features

- ✅ Fully accessible (ARIA labels, keyboard navigation, focus management)
- ✅ Responsive design (mobile and desktop)
- ✅ Matches application theme (dark mode support)
- ✅ Loading states during deletion
- ✅ Promise-based API for easy integration
- ✅ Customizable messages and button text
- ✅ Escape key support

## Registration

The component is already registered globally in `App.vue`. No additional setup required!

## Basic Usage

### 1. Import the composable

```javascript
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
```

### 2. Use in your component

```vue
<script setup>
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import { useNotification } from '@/composables/useNotification'

const { confirmDelete } = useDeleteConfirmation()
const notify = useNotification()

const handleDelete = async (itemId) => {
  try {
    await confirmDelete(
      itemId,
      async () => {
        // Your delete logic here
        await deleteItem(itemId)
      }
    )
    // Success - item was deleted
    notify.success('Item deleted successfully')
  } catch (error) {
    // User cancelled or error occurred
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete item')
    }
  }
}
</script>
```

## Advanced Usage

### Custom Messages

```javascript
await confirmDelete(
  itemId,
  async () => {
    await deleteItem(itemId)
  },
  {
    title: 'Delete Template?',
    message: 'This will permanently delete the template and all associated content.',
    itemName: template.name,
    confirmText: 'Yes, Delete Template',
    cancelText: 'Keep Template'
  }
)
```

### With Loading State

The component automatically shows a loading state while your delete callback is executing:

```javascript
await confirmDelete(
  itemId,
  async () => {
    // This will show loading state automatically
    await api.delete(`/items/${itemId}`)
  },
  {
    loadingText: 'Removing item...'
  }
)
```

## Examples

### Example 1: Delete from a list

```vue
<template>
  <button @click="handleDelete(item.id)">
    Delete
  </button>
</template>

<script setup>
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import { itemsAPI } from '@/services/api'
import { useNotification } from '@/composables/useNotification'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['deleted'])

const { confirmDelete } = useDeleteConfirmation()
const notify = useNotification()

const handleDelete = async (itemId) => {
  try {
    await confirmDelete(
      itemId,
      async () => {
        await itemsAPI.delete(itemId)
      },
      {
        title: 'Delete Item?',
        message: 'This action cannot be undone.',
        itemName: props.item.name
      }
    )
    notify.success('Item deleted')
    emit('deleted', itemId)
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete item')
    }
  }
}
</script>
```

### Example 2: Delete with confirmation message

```vue
<script setup>
const handleDelete = async (templateId) => {
  try {
    await confirmDelete(
      templateId,
      async () => {
        await templatesStore.deleteTemplate(templateId)
      },
      {
        title: 'Delete Template?',
        message: 'This will permanently delete the template and all its layers, widgets, and content. This action cannot be undone.',
        itemName: template.name,
        confirmText: 'Yes, Delete Template',
        cancelText: 'Cancel'
      }
    )
    notify.success('Template deleted successfully')
    router.push('/templates')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete template')
    }
  }
}
</script>
```

## API Reference

### `confirmDelete(itemId, callback, options)`

**Parameters:**

- `itemId` (string|number, optional): The ID of the item to delete (for display purposes)
- `callback` (Function, required): Async function to execute when confirmed
- `options` (Object, optional): Configuration options
  - `title` (string): Custom title (default: "Confirm Deletion")
  - `message` (string): Custom message (default: "Are you sure you want to delete this item? This action cannot be undone.")
  - `itemName` (string): Name of the item to display
  - `confirmText` (string): Text for confirm button (default: "Yes, Delete")
  - `cancelText` (string): Text for cancel button (default: "Cancel")
  - `loadingText` (string): Text shown during deletion (default: "Deleting...")

**Returns:** Promise that resolves if confirmed, rejects if cancelled or on error

## Accessibility

- Full keyboard support (Escape to cancel, Tab navigation)
- ARIA labels and roles
- Focus management (returns focus to trigger element)
- Screen reader friendly

## Styling

The component uses your application's existing theme:
- `btn-danger` for delete button
- `btn-outline` for cancel button
- Theme-aware colors (dark mode support)
- Responsive design (mobile-first)

## Migration from `confirm()`

**Before:**
```javascript
if (confirm('Are you sure you want to delete this item?')) {
  await deleteItem(itemId)
}
```

**After:**
```javascript
try {
  await confirmDelete(itemId, async () => {
    await deleteItem(itemId)
  })
} catch (error) {
  // User cancelled
}
```

