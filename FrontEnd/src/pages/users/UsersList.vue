<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Users & Roles</h1>
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
            <span class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs capitalize">{{ value }}</span>
          </template>
          <template #actions="{ row }">
            <router-link
              :to="`/users/${row.id}`"
              class="text-indigo-600 hover:text-indigo-900 mr-3"
            >
              View
            </router-link>
            <button
              @click="handleEdit(row)"
              class="text-blue-600 hover:text-blue-900 mr-3"
            >
              Edit
            </button>
            <button
              @click="handleChangeRole(row)"
              class="text-purple-600 hover:text-purple-900 mr-3"
            >
              Change Role
            </button>
            <button
              @click="handleDelete(row)"
              class="text-red-600 hover:text-red-900"
            >
              Delete
            </button>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input v-model="form.username" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="form.email" type="email" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input v-model="form.full_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div v-if="!showEditModal">
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input v-model="form.password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select v-model="form.role" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="Viewer">Viewer</option>
              <option value="Manager">Manager</option>
              <option value="Operator">Operator</option>
              <option value="Admin">Admin</option>
              <option value="SuperAdmin">SuperAdmin</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Organization</label>
            <input v-model="form.organization_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
      
      <!-- Change Role Modal -->
      <Modal :show="showRoleModal" title="Change Role" @close="showRoleModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">New Role</label>
            <select v-model="roleForm.role" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
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
          <button type="button" @click="showRoleModal = false" class="px-4 py-2 border border-gray-300 rounded-lg">
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
import { useUsersStore } from '@/stores/users'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const usersStore = useUsersStore()
const toastStore = useToastStore()

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
  if (confirm(`Delete user "${row.username}"?`)) {
    try {
      await usersStore.deleteUser(row.id)
      toastStore.success('User deleted')
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to delete user'
      toastStore.error(errorMsg)
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
      toastStore.success('User updated')
    } else {
      await usersStore.createUser(form.value)
      toastStore.success('User created')
    }
    closeModal()
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Operation failed'
    toastStore.error(errorMsg)
  }
}

const handleRoleSubmit = async () => {
  try {
    await usersStore.changeRole(roleChangingUser.value.id, roleForm.value.role)
    toastStore.success('Role changed')
    showRoleModal.value = false
    roleChangingUser.value = null
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to change role'
    toastStore.error(errorMsg)
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
