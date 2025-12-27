<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-primary">Users & Roles</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Create User
        </button>
      </div>
      
      <Card>
        <div v-if="usersStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="usersStore.error" class="text-center py-8 text-red-600">
          {{ usersStore.error }}
        </div>
        <Table
          v-else
          :columns="columns"
          :data="usersStore.users"
          :actions="['view', 'edit', 'delete']"
          @view="handleView"
          @edit="handleEdit"
          @delete="handleDelete"
        >
          <template #cell-role="{ value }">
            <span class="badge-primary px-2 py-1 rounded text-xs capitalize">{{ value }}</span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center justify-end gap-1">
              <router-link
                :to="`/users/${row.id}`"
                class="action-btn-view"
                title="View"
              >
                <EyeIcon class="w-4 h-4" />
              </router-link>
              <button
                @click="handleEdit(row)"
                class="action-btn-edit"
                title="Edit"
              >
                <PencilIcon class="w-4 h-4" />
              </button>
              <button
                @click="handleChangeRole(row)"
                class="action-btn-role"
                title="Change Role"
              >
                <ShieldCheckIcon class="w-4 h-4" />
              </button>
              <button
                @click="handleDelete(row)"
                class="action-btn-delete"
                title="Delete"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </template>
        </Table>
      </Card>
      
      <!-- Create/Edit Modal -->
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit User' : 'Create User'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Username</label>
            <input v-model="form.username" type="text" required class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Email</label>
            <input v-model="form.email" type="email" required class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Full Name</label>
            <input v-model="form.full_name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div v-if="!showEditModal">
            <label class="label-base block text-sm mb-1">Password</label>
            <input v-model="form.password" type="password" required class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Role</label>
            <select v-model="form.role" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="Viewer">Viewer</option>
              <option value="Manager">Manager</option>
              <option value="Operator">Operator</option>
              <option value="Admin">Admin</option>
              <option value="SuperAdmin">SuperAdmin</option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Organization</label>
            <input v-model="form.organization_name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
      
      <!-- Change Role Modal -->
      <Modal :show="showRoleModal" title="Change Role" @close="showRoleModal = false">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">New Role</label>
            <select v-model="roleForm.role" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="Viewer">Viewer</option>
              <option value="Manager">Manager</option>
              <option value="Operator">Operator</option>
              <option value="Admin">Admin</option>
              <option value="SuperAdmin">SuperAdmin</option>
            </select>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleRoleSubmit" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Change Role
          </button>
          <button type="button" @click="showRoleModal = false" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { EyeIcon, PencilIcon, TrashIcon, ShieldCheckIcon } from '@heroicons/vue/24/outline'
import { useUsersStore } from '@/stores/users'
import { useNotification } from '@/composables/useNotification'
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const usersStore = useUsersStore()
const notify = useNotification()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showRoleModal = ref(false)
const editingUser = ref(null)
const roleChangingUser = ref(null)

const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'Viewer',
  organization_name: '',
})

const roleForm = ref({
  role: 'Viewer',
})

const columns = [
  { key: 'username', label: 'Username' },
  { key: 'email', label: 'Email' },
  { key: 'full_name', label: 'Full Name' },
  { key: 'role', label: 'Role' },
  { key: 'organization_name', label: 'Organization' },
]

const handleView = (row) => {
  router.push(`/users/${row.id}`)
}

const handleEdit = (row) => {
  editingUser.value = row
  form.value = {
    username: row.username || '',
    email: row.email || '',
    full_name: row.full_name || '',
    password: '',
    role: row.role || 'Viewer',
    organization_name: row.organization_name || '',
  }
  showEditModal.value = true
}

const handleChangeRole = (row) => {
  roleChangingUser.value = row
  roleForm.value.role = row.role || 'Viewer'
  showRoleModal.value = true
}

const handleDelete = async (row) => {
  try {
    const { confirmDelete } = useDeleteConfirmation()
    await confirmDelete(
      row.id,
      async () => {
        await usersStore.deleteUser(row.id)
      },
      {
        title: 'Delete User?',
        message: 'This will permanently delete the user account and all associated data. This action cannot be undone.',
        itemName: row.username,
        confirmText: 'Yes, Delete User',
        cancelText: 'Cancel'
      }
    )
    notify.success('User deleted successfully')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to delete user'
      notify.error(errorMsg)
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      const updateData = { ...form.value }
      delete updateData.password // Don't send password if empty
      if (!updateData.password) {
        delete updateData.password
      }
      await usersStore.updateUser(editingUser.value.id, updateData)
      notify.success('User updated')
    } else {
      await usersStore.createUser(form.value)
      notify.success('User created')
    }
    closeModal()
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Operation failed'
    notify.error(errorMsg)
  }
}

const handleRoleSubmit = async () => {
  try {
    await usersStore.changeRole(roleChangingUser.value.id, roleForm.value.role)
    notify.success('Role changed')
    showRoleModal.value = false
    roleChangingUser.value = null
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to change role'
    notify.error(errorMsg)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingUser.value = null
  form.value = {
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'Viewer',
    organization_name: '',
  }
}

onMounted(async () => {
  await usersStore.fetchUsers()
})
</script>
