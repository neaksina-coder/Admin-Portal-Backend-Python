<script setup lang="ts">
import { formatDate } from '@core/utils/formatters'

definePage({
  meta: {
    action: 'read',
    subject: 'Apps',
  },
})

type ContactInquiryStatus = 'new' | 'in_progress' | 'replied' | 'closed'

type ContactInquiry = {
  id: number
  businessId?: number
  name: string
  email: string
  phone?: string
  company?: string
  serviceInterest?: string
  subject?: string
  message?: string
  status?: ContactInquiryStatus
  assignedToUserId?: number | null
  source?: string
  createdAt?: string
  updatedAt?: string
  repliedAt?: string
}

type AdminUser = {
  id: number
  name: string
  email?: string
}

type BusinessItem = {
  id: number
  name: string
}

const BUSINESS_ID = Number(import.meta.env.VITE_BUSINESS_ID ?? 1)

const filters = reactive({
  businessId: BUSINESS_ID || null,
  status: '',
  q: '',
})

const itemsPerPage = ref(20)
const page = ref(1)
const sortBy = ref()
const orderBy = ref()

const updateOptions = (options: any) => {
  sortBy.value = options.sortBy[0]?.key
  orderBy.value = options.sortBy[0]?.order
}

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Subject', key: 'subject' },
  { title: 'Status', key: 'status' },
  { title: 'Assigned', key: 'assignedToUserId' },
  { title: 'Created', key: 'createdAt' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const statusOptions: { title: string; value: ContactInquiryStatus | '' }[] = [
  { title: 'All', value: '' },
  { title: 'New', value: 'new' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Replied', value: 'replied' },
  { title: 'Closed', value: 'closed' },
]

const resolveStatusColor = (status?: ContactInquiryStatus) => {
  if (status === 'new')
    return 'primary'
  if (status === 'in_progress')
    return 'warning'
  if (status === 'replied')
    return 'success'
  if (status === 'closed')
    return 'secondary'

  return 'secondary'
}

const normalizeInquiry = (item: any): ContactInquiry => {
  if (!item || typeof item !== 'object') {
    return {
      id: 0,
      name: 'Unknown',
      email: '',
    }
  }

  return {
    id: Number(item.id ?? item.inquiryId ?? item.inquiry_id ?? 0),
    businessId: Number(item.businessId ?? item.business_id ?? item.business?.id ?? 0) || undefined,
    name: item.name ?? item.fullName ?? item.full_name ?? 'Unknown',
    email: item.email ?? item.fromEmail ?? item.from_email ?? '',
    phone: item.phone ?? item.phoneNumber ?? item.phone_number ?? '',
    company: item.company ?? item.companyName ?? item.company_name ?? '',
    serviceInterest: item.serviceInterest ?? item.service_interest ?? item.service ?? '',
    subject: item.subject ?? item.title ?? '',
    message: item.message ?? item.body ?? item.content ?? '',
    status: item.status ?? 'new',
    assignedToUserId: item.assignedToUserId ?? item.assigned_to_user_id ?? null,
    source: item.source ?? 'public_web',
    createdAt: item.createdAt ?? item.created_at ?? item.created ?? item.timestamp ?? null,
    updatedAt: item.updatedAt ?? item.updated_at ?? null,
    repliedAt: item.repliedAt ?? item.replied_at ?? null,
  }
}

const { data: inquiriesData, execute: fetchInquiries, isFetching } = await useApi<any>(createUrl('/contact-inquiries', {
  query: {
    businessId: computed(() => filters.businessId || undefined),
    status: computed(() => filters.status || undefined),
    q: computed(() => filters.q || undefined),
    skip: computed(() => (page.value - 1) * itemsPerPage.value),
    limit: itemsPerPage,
    sortBy,
    orderBy,
  },
}))

const { data: businessesData } = await useApi<any>(createUrl('/businesses', {
  query: {
    skip: 0,
    limit: 500,
  },
}))

const { data: adminsData } = await useApi<any>('/users/admins')

const businesses = computed<BusinessItem[]>(() => {
  const payload = businessesData.value
  const list = payload?.items ?? payload?.data ?? payload?.businesses ?? payload?.results ?? []

  if (!Array.isArray(list))
    return []

  return list
    .map((item: any) => {
      if (!item)
        return null

      const id = Number(item.id ?? item.businessId ?? item.business_id ?? 0)
      if (!id)
        return null

      const name = item.name ?? item.businessName ?? item.business_name ?? `Business ${id}`

      return {
        id,
        name: String(name),
      }
    })
    .filter((item: BusinessItem | null): item is BusinessItem => !!item)
})

const businessOptions = computed(() => [
  { title: 'All', value: null },
  ...businesses.value.map(business => ({
    title: business.name,
    value: business.id,
  })),
])

const admins = computed<AdminUser[]>(() => {
  const payload = adminsData.value
  const list = payload?.items ?? payload?.data ?? payload?.admins ?? payload?.users ?? payload?.results ?? []

  if (!Array.isArray(list))
    return []

  return list
    .map((item: any) => {
      if (!item)
        return null

      const id = Number(item.id ?? item.userId ?? item.user_id ?? 0)
      if (!id)
        return null

      const name = item.name ?? item.username ?? item.fullName ?? item.full_name ?? item.email ?? `Admin ${id}`

      return {
        id,
        name: String(name),
        email: item.email ?? item.userEmail ?? item.user_email ?? undefined,
      }
    })
    .filter((item: AdminUser | null): item is AdminUser => !!item)
})

const adminOptions = computed(() => admins.value.map(admin => ({
  title: admin.name,
  value: admin.id,
})))

const getAdminName = (id?: number | null) => {
  if (!id)
    return '-'
  return admins.value.find(admin => admin.id === id)?.name ?? String(id)
}

const inquiries = computed<ContactInquiry[]>(() => {
  const payload = inquiriesData.value
  const list = payload?.items ?? payload?.data ?? payload?.contactInquiries ?? payload?.results ?? []

  if (!Array.isArray(list))
    return []

  return list.map(normalizeInquiry).filter(item => item.id)
})

const totalInquiries = computed(() => {
  const payload = inquiriesData.value
  return payload?.total ?? payload?.count ?? payload?.totalItems ?? inquiries.value.length
})

const isDetailOpen = ref(false)
const activeInquiry = ref<ContactInquiry | null>(null)
const isLoadingDetail = ref(false)

const isReplyDialogOpen = ref(false)
const replySubject = ref('')
const replyBody = ref('')
const isSendingReply = ref(false)

const statusUpdate = reactive({
  status: 'new' as ContactInquiryStatus,
  assignedToUserId: null as number | null,
})
const isSavingStatus = ref(false)

const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const showSnackbar = (text: string, color: string = 'success') => {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

const openInquiryDetail = async (item: ContactInquiry) => {
  activeInquiry.value = item
  isDetailOpen.value = true
  isLoadingDetail.value = true

  try {
    const response = await $api(`/contact-inquiries/${item.id}`)
    const payload = response?.data ?? response ?? {}
    const data = payload?.data ?? payload?.inquiry ?? payload

    activeInquiry.value = normalizeInquiry(data)
  }
  catch (error) {
    showSnackbar('Failed to load inquiry details.', 'error')
  }
  finally {
    isLoadingDetail.value = false
  }
}

watch(activeInquiry, value => {
  if (!value)
    return

  statusUpdate.status = value.status ?? 'new'
  statusUpdate.assignedToUserId = value.assignedToUserId ?? null
}, { immediate: true })

const saveInquiryUpdate = async () => {
  if (!activeInquiry.value)
    return

  try {
    isSavingStatus.value = true

    const payload: Record<string, any> = {
      status: statusUpdate.status,
      assignedToUserId: statusUpdate.assignedToUserId ?? null,
    }

    await $api(`/contact-inquiries/${activeInquiry.value.id}`, {
      method: 'PUT',
      body: payload,
    })

    activeInquiry.value = {
      ...activeInquiry.value,
      status: statusUpdate.status,
      assignedToUserId: statusUpdate.assignedToUserId ?? null,
    }

    showSnackbar('Inquiry updated.')
    fetchInquiries()
  }
  catch (error) {
    showSnackbar('Failed to update inquiry.', 'error')
  }
  finally {
    isSavingStatus.value = false
  }
}

const openReplyDialog = (item: ContactInquiry) => {
  activeInquiry.value = item
  replySubject.value = item.subject ? `Re: ${item.subject}` : 'Re: Your inquiry'
  replyBody.value = ''
  isReplyDialogOpen.value = true
}

const sendReply = async () => {
  if (!activeInquiry.value)
    return

  if (!replySubject.value.trim() || !replyBody.value.trim()) {
    showSnackbar('Please provide a subject and reply message.', 'error')
    return
  }

  try {
    isSendingReply.value = true
    await $api(`/contact-inquiries/${activeInquiry.value.id}/reply`, {
      method: 'POST',
      body: {
        subject: replySubject.value.trim(),
        body: replyBody.value.trim(),
      },
    })

    isReplyDialogOpen.value = false
    statusUpdate.status = 'replied'
    activeInquiry.value = {
      ...activeInquiry.value,
      status: 'replied',
      repliedAt: new Date().toISOString(),
    }

    showSnackbar('Reply sent.')
    fetchInquiries()
  }
  catch (error) {
    showSnackbar('Failed to send reply.', 'error')
  }
  finally {
    isSendingReply.value = false
  }
}
</script>

<template>
  <section>
    <VCard class="mb-6">
      <VCardItem>
        <VCardTitle>Contact Inquiries</VCardTitle>
      </VCardItem>

      <VCardText>
        <VRow>
          <VCol cols="12" md="4">
            <AppSelect
              v-model="filters.businessId"
              label="Business"
              placeholder="Select business"
              :items="businessOptions"
              item-title="title"
              item-value="value"
            />
          </VCol>
          <VCol cols="12" md="4">
            <AppSelect
              v-model="filters.status"
              label="Status"
              :items="statusOptions"
              item-title="title"
              item-value="value"
            />
          </VCol>
          <VCol cols="12" md="4">
            <AppTextField
              v-model="filters.q"
              label="Search"
              placeholder="Name, email, subject..."
            />
          </VCol>
          <VCol cols="12" class="d-flex align-end gap-3">
            <VBtn color="primary" @click="fetchInquiries()">
              Search
            </VBtn>
            <VBtn
              variant="tonal"
              color="secondary"
              prepend-icon="tabler-refresh"
              :loading="isFetching"
              @click="fetchInquiries()"
            >
              Refresh
            </VBtn>
          </VCol>
        </VRow>
      </VCardText>

      <VDivider />

      <VDataTableServer
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        :items-per-page-options="[
          { value: 20, title: '20' },
          { value: 50, title: '50' },
          { value: 100, title: '100' },
        ]"
        :items="inquiries"
        :items-length="totalInquiries"
        :headers="headers"
        class="text-no-wrap"
        @update:options="updateOptions"
      >
        <template #item.id="{ item }">
          <span class="text-high-emphasis font-weight-medium">#{{ item.id }}</span>
        </template>

        <template #item.subject="{ item }">
          <span>{{ item.subject || '-' }}</span>
        </template>

        <template #item.status="{ item }">
          <VChip
            size="small"
            label
            class="text-capitalize"
            :color="resolveStatusColor(item.status)"
          >
            {{ item.status || 'new' }}
          </VChip>
        </template>

        <template #item.assignedToUserId="{ item }">
          <span>{{ getAdminName(item.assignedToUserId) }}</span>
        </template>

        <template #item.createdAt="{ item }">
          <span>{{ item.createdAt ? formatDate(item.createdAt) : '-' }}</span>
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex gap-2">
            <IconBtn @click="openInquiryDetail(item)">
              <VIcon icon="tabler-eye" />
            </IconBtn>
            <IconBtn @click="openReplyDialog(item)">
              <VIcon icon="tabler-reply" />
            </IconBtn>
          </div>
        </template>
      </VDataTableServer>
    </VCard>

    <VDialog v-model="isDetailOpen" max-width="900">
      <VCard>
        <VCardItem>
          <VCardTitle>Inquiry Details</VCardTitle>
        </VCardItem>
        <VProgressLinear
          v-if="isLoadingDetail"
          indeterminate
          height="3"
        />
        <VCardText v-if="activeInquiry">
          <VRow class="mb-2">
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Name</div>
              <div class="text-body-1">{{ activeInquiry.name }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Email</div>
              <div class="text-body-1">{{ activeInquiry.email }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Phone</div>
              <div class="text-body-1">{{ activeInquiry.phone || '-' }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Company</div>
              <div class="text-body-1">{{ activeInquiry.company || '-' }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Service Interest</div>
              <div class="text-body-1">{{ activeInquiry.serviceInterest || '-' }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Subject</div>
              <div class="text-body-1">{{ activeInquiry.subject || '-' }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Status</div>
              <VChip
                size="small"
                label
                class="text-capitalize"
                :color="resolveStatusColor(activeInquiry.status)"
              >
                {{ activeInquiry.status || 'new' }}
              </VChip>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Assigned To</div>
              <div class="text-body-1">{{ getAdminName(activeInquiry.assignedToUserId) }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Created</div>
              <div class="text-body-1">{{ activeInquiry.createdAt ? formatDate(activeInquiry.createdAt) : '-' }}</div>
            </VCol>
            <VCol cols="12" md="6">
              <div class="text-sm text-disabled">Replied</div>
              <div class="text-body-1">{{ activeInquiry.repliedAt ? formatDate(activeInquiry.repliedAt) : '-' }}</div>
            </VCol>
          </VRow>

          <VDivider class="my-4" />

          <div class="text-sm text-disabled mb-2">Message</div>
          <div class="text-body-1 white-space-pre-wrap">
            {{ activeInquiry.message || '-' }}
          </div>

          <VDivider class="my-4" />

          <div class="text-sm text-disabled mb-2">Update Status</div>
          <VRow>
            <VCol cols="12" md="6">
              <AppSelect
                v-model="statusUpdate.status"
                label="Status"
                :items="statusOptions.filter(option => option.value)"
                item-title="title"
                item-value="value"
              />
            </VCol>
            <VCol cols="12" md="6">
              <AppSelect
                v-model="statusUpdate.assignedToUserId"
                label="Assigned To"
                placeholder="Select admin"
                :items="adminOptions"
                item-title="title"
                item-value="value"
                clearable
              />
            </VCol>
          </VRow>
        </VCardText>
        <VCardText class="d-flex justify-end gap-3">
          <VBtn variant="tonal" color="secondary" @click="isDetailOpen = false">
            Close
          </VBtn>
          <VBtn
            variant="tonal"
            color="primary"
            :disabled="!activeInquiry"
            @click="activeInquiry && openReplyDialog(activeInquiry)"
          >
            Reply
          </VBtn>
          <VBtn
            color="primary"
            :loading="isSavingStatus"
            :disabled="!activeInquiry"
            @click="saveInquiryUpdate"
          >
            Save Changes
          </VBtn>
        </VCardText>
      </VCard>
    </VDialog>

    <VDialog v-model="isReplyDialogOpen" max-width="720">
      <VCard>
        <VCardItem>
          <VCardTitle>Reply to Inquiry</VCardTitle>
        </VCardItem>
        <VCardText v-if="activeInquiry">
          <div class="text-sm text-disabled mb-2">To</div>
          <div class="text-body-1 mb-4">
            {{ activeInquiry.email }}
          </div>
          <AppTextField
            v-model="replySubject"
            label="Subject"
            placeholder="Reply subject"
            class="mb-4"
          />
          <AppTextarea
            v-model="replyBody"
            label="Reply message"
            rows="6"
            placeholder="Write your reply..."
          />
        </VCardText>
        <VCardText class="d-flex justify-end gap-3">
          <VBtn variant="tonal" color="secondary" @click="isReplyDialogOpen = false">
            Cancel
          </VBtn>
          <VBtn color="primary" :loading="isSendingReply" @click="sendReply">
            Send Reply
          </VBtn>
        </VCardText>
      </VCard>
    </VDialog>

    <VSnackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="3000"
      location="top"
    >
      {{ snackbarText }}
    </VSnackbar>
  </section>
</template>

<style scoped lang="scss">
.white-space-pre-wrap {
  white-space: pre-wrap;
}
</style>
