<template>
  <AppLayout>
    <div v-if="loading" class="template-editor h-screen w-full flex items-center justify-center bg-gray-900 text-white overflow-hidden">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p class="text-gray-400">Loading template...</p>
      </div>
    </div>
    <div v-else class="template-editor h-screen w-full flex flex-col bg-gray-900 text-white overflow-hidden">
      <!-- Top Toolbar -->
      <div class="flex items-center justify-between px-4 py-3 bg-card border-b border-border-color">
        <div class="flex items-center gap-3">
          <button
            @click="goBack"
            class="btn-outline px-3 py-2 active:scale-95 rounded-lg text-sm font-medium transition-all duration-400 flex items-center gap-2"
            title="Back to Templates List"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to List
          </button>
          <h1 class="text-xl font-semibold text-primary">{{ templateName || 'Untitled Template' }}</h1>
          <button
            @click="saveTemplate"
            :disabled="saving"
            class="btn-primary px-4 py-2 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all duration-400"
          >
            {{ saving ? 'Saving...' : 'Save Template' }}
          </button>
          <button
            @click="exportJSON"
            class="btn-outline px-4 py-2 active:scale-95 rounded-lg text-sm font-medium transition-all duration-400"
          >
            Export JSON
          </button>
          <button
            @click="deleteSelectedWidget"
            :disabled="!selectedWidgetId"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-400 border border-red-500/60 text-red-300 hover:bg-red-500/10 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Delete selected object"
          >
            Delete Object
          </button>
          <button
            v-if="templateId"
            @click="handlePushToScreen"
            :disabled="saving || pushing"
            class="btn-secondary px-4 py-2 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all duration-400 flex items-center gap-2"
          >
            <svg v-if="!pushing" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            {{ pushing ? 'Pushing...' : 'Push to Screen' }}
          </button>
        </div>
        <div class="flex items-center gap-2 text-sm text-muted">
          <button
            @click="leftPanelCollapsed = !leftPanelCollapsed"
            class="btn-outline px-2 py-1 rounded text-xs"
            :title="leftPanelCollapsed ? 'Expand widget panel' : 'Collapse widget panel'"
          >
            {{ leftPanelCollapsed ? 'Show Tools' : 'Hide Tools' }}
          </button>
          <button
            @click="rightPanelCollapsed = !rightPanelCollapsed"
            class="btn-outline px-2 py-1 rounded text-xs"
            :title="rightPanelCollapsed ? 'Expand inspector panel' : 'Collapse inspector panel'"
          >
            {{ rightPanelCollapsed ? 'Show Inspector' : 'Hide Inspector' }}
          </button>
        </div>
      </div>

      <!-- Main Editor Area -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Left Sidebar: Widget Library -->
        <div
          class="hidden lg:block bg-card border-r border-border-color overflow-y-auto custom-scrollbar scroll-container transition-all duration-200"
          :class="leftPanelCollapsed ? 'w-16' : 'w-56'"
        >
          <div class="bg-card border-b border-border-color px-4 py-3 sticky top-0 z-10 backdrop-blur-sm">
            <h2 v-if="!leftPanelCollapsed" class="text-lg font-semibold text-primary">Widget Library</h2>
            <h2 v-else class="text-xs font-semibold text-primary uppercase tracking-wide">Tools</h2>
          </div>
          <div class="p-2" :class="leftPanelCollapsed ? 'space-y-1' : 'p-4'">
            <div class="space-y-2">
              <button
                @click="addWidget('text')"
                class="w-full px-4 py-3 bg-card hover:bg-card active:scale-95 rounded-lg text-left text-primary transition-all duration-400 flex items-center gap-2 font-medium border border-border-color hover:border-accent-color/50"
                style="--accent-color: var(--accent-color);"
                :title="leftPanelCollapsed ? 'Add Text' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Text</span>
              </button>
              <button
                @click="addWidget('image')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Image' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Image</span>
              </button>
              <button
                @click="addWidget('video')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Video' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Video</span>
              </button>
              <button
                @click="addWidget('clock')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Clock' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Clock</span>
              </button>
              <button
                @click="addWidget('date')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Date' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Date</span>
              </button>
              <button
                @click="addWidget('webview')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Webview' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12H3m0 0l4-4m-4 4l4 4m14-4l-4-4m4 4l-4 4" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Webview</span>
              </button>
              <button
                @click="addWidget('chart')"
                class="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 active:scale-95 rounded-lg text-left text-white transition-all duration-200 flex items-center gap-2 font-medium"
                :title="leftPanelCollapsed ? 'Add Chart' : ''"
              >
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3v18h18M8 13l3-3 3 2 4-5" />
                </svg>
                <span v-if="!leftPanelCollapsed">Add Chart</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Center: Canvas Area -->
        <div class="flex-1 flex flex-col bg-gray-900 overflow-hidden">
          <div
            ref="canvasContainer"
            class="relative flex-1 overflow-hidden bg-gray-700 flex items-center justify-center"
            @wheel.prevent="handleWheel"
          >
            <!-- Monitor Frame (Wall-Mounted Display) -->
            <div
              ref="canvasWrapper"
              class="relative monitor-frame"
              :style="{
                padding: '12px',
                width: `${canvasWidth + 24}px`,
                height: `${canvasHeight + 24}px`,
                transform: `scale(${scale})`,
                transformOrigin: 'center center',
                flexShrink: 0
              }"
            >
              <!-- Power Indicator Light -->
              <div class="power-indicator absolute bottom-3 right-5 w-2 h-2 bg-green-400 rounded-full"></div>
              
              <!-- Canvas Background -->
              <div
                ref="canvasArea"
                class="relative canvas-area rounded overflow-hidden"
                :style="{
                  width: `${canvasWidth}px`,
                  height: `${canvasHeight}px`,
                  backgroundImage: canvasBackgroundImage
                        ? `url(${canvasBackgroundImage})`
                        : undefined,
                  backgroundSize: canvasBackgroundImage ? 'cover' : undefined,
                  backgroundColor: canvasBackgroundImage ? canvasBackgroundColor : undefined
                }"
              >
                <!-- Empty State Watermark -->
                <div
                  v-if="widgets.length === 0"
                  class="absolute inset-0 flex items-center justify-center pointer-events-none"
                >
                  <span class="text-muted text-lg font-light opacity-50 select-none">
                    Drag widgets here to start
                  </span>
                </div>
                <!-- Render Widgets -->
                <div
                  v-for="widget in sortedWidgetsByZIndex"
                  :key="widget.id"
                  :ref="el => setWidgetRef(el, widget.id)"
                  :data-widget-id="widget.id"
                  class="widget-element absolute cursor-move"
                  :class="{ 'widget-selected': selectedWidgetId === widget.id }"
                  :style="getWidgetStyle(widget)"
                  @click.stop="selectWidget(widget.id)"
                >
                  <!-- Widget Content Preview -->
                  <WidgetPreview :widget="widget" />
                </div>

                <!-- Moveable Component -->
                <Moveable
                  v-if="selectedWidget"
                  ref="moveableRef"
                  :target="selectedWidgetElement"
                  :draggable="true"
                  :resizable="true"
                  :rotatable="true"
                  :scalable="false"
                  :snappable="true"
                  :snapThreshold="5"
                  :snapGap="false"
                  :snapElement="true"
                  :snapVertical="true"
                  :snapHorizontal="true"
                  :snapCenter="true"
                  :elementGuidelines="widgetElements"
                  :bounds="canvasBounds"
                  :zoom="1 / scale"
                  :persistRect="true"
                  :keepRatio="false"
                  :edge="false"
                  :throttleDrag="0"
                  :throttleResize="1"
                  :throttleRotate="0"
                  @dragStart="handleDragMoveableStart"
                  @drag="handleDrag"
                  @dragEnd="handleDragEnd"
                  @resizeStart="handleResizeStart"
                  @resize="handleResize"
                  @resizeEnd="handleResizeEnd"
                  @rotate="handleRotate"
                  @rotateEnd="handleRotateEnd"
                />
              </div>
            </div>
            <div class="absolute bottom-4 right-4 z-20 flex items-center gap-2 rounded-lg border border-border-color bg-card/95 px-3 py-2 text-xs text-muted">
              <span>{{ canvasWidth }}×{{ canvasHeight }}</span>
              <span>|</span>
              <button class="btn-outline px-2 py-1 rounded" @click="zoomOut">-</button>
              <span class="w-10 text-center">{{ Math.round(scale * 100) }}%</span>
              <button class="btn-outline px-2 py-1 rounded" @click="zoomIn">+</button>
              <button class="btn-outline px-2 py-1 rounded" @click="calculateScale">Fit</button>
            </div>
          </div>
        </div>

        <!-- Right Sidebar: Properties Panel -->
        <div
          class="hidden lg:block bg-card border-l border-border-color overflow-y-auto custom-scrollbar scroll-container transition-all duration-200"
          :class="rightPanelCollapsed ? 'w-14' : 'w-80'"
        >
          <div class="bg-card border-b border-border-color px-4 py-3 sticky top-0 z-10 backdrop-blur-sm">
            <h2 v-if="!rightPanelCollapsed" class="text-lg font-semibold text-primary">Inspector</h2>
            <h2 v-else class="text-xs font-semibold text-primary uppercase tracking-wide">Panel</h2>
          </div>
          <div v-if="!rightPanelCollapsed" class="p-4">
            <div class="mb-4 grid grid-cols-2 rounded-lg bg-gray-800/50 p-1">
              <button
                @click="rightPanelTab = 'properties'"
                :class="rightPanelTab === 'properties' ? 'bg-accent-color text-white' : 'text-muted hover:text-primary'"
                class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors"
              >
                Properties
              </button>
              <button
                @click="rightPanelTab = 'layers'"
                :class="rightPanelTab === 'layers' ? 'bg-accent-color text-white' : 'text-muted hover:text-primary'"
                class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors"
              >
                Layers
              </button>
            </div>

            <div v-if="rightPanelTab === 'properties' && selectedWidget" class="space-y-6">
              <!-- Common Properties -->
              <div>
                <h3 class="text-sm font-semibold mb-3 text-muted uppercase">Position & Size</h3>
                <div class="space-y-3">
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="block text-xs font-medium text-muted mb-1.5">X (px)</label>
                      <input
                        :value="Math.round(selectedWidget.x)"
                        type="number"
                        class="input-base w-full px-3 py-2 text-sm"
                        @input="updateWidgetProperty('x', $event.target.value)"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-muted mb-1.5">Y (px)</label>
                      <input
                        :value="Math.round(selectedWidget.y)"
                        type="number"
                        class="input-base w-full px-3 py-2 text-sm"
                        @input="updateWidgetProperty('y', $event.target.value)"
                      />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="block text-xs font-medium text-muted mb-1.5">Width (px)</label>
                      <input
                        :value="Math.round(selectedWidget.width)"
                        type="number"
                        class="input-base w-full px-3 py-2 text-sm"
                        @input="updateWidgetProperty('width', $event.target.value)"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-muted mb-1.5">Height (px)</label>
                      <input
                        :value="Math.round(selectedWidget.height)"
                        type="number"
                        class="input-base w-full px-3 py-2 text-sm"
                        @input="updateWidgetProperty('height', $event.target.value)"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-muted mb-1.5">Rotation (°)</label>
                    <input
                      v-model.number="selectedWidget.rotation"
                      type="number"
                      step="1"
                      class="input-base w-full px-3 py-2 text-sm"
                      @input="updateWidgetProperty('rotation', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-muted mb-1.5">Z-Index</label>
                    <input
                      v-model.number="selectedWidget.zIndex"
                      type="number"
                      class="input-base w-full px-3 py-2 text-sm"
                      @input="updateWidgetProperty('zIndex', $event.target.value)"
                    />
                  </div>
                </div>
              </div>

              <!-- Text Widget Properties -->
              <div v-if="selectedWidget.type === 'text'">
                <h3 class="text-sm font-semibold mb-3 text-muted uppercase">Text Properties</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-muted mb-1.5">Content</label>
                    <textarea
                      v-model="selectedWidget.content"
                      rows="3"
                      class="textarea-base w-full px-3 py-2 text-sm"
                      @input="updateWidgetProperty('content', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-muted mb-1.5">Font Family</label>
                    <select
                      v-model="selectedWidget.style.fontFamily"
                      class="select-base w-full px-3 py-2 text-sm"
                      @change="updateWidgetStyle('fontFamily', $event.target.value)"
                    >
                      <option value="Arial, sans-serif">Arial</option>
                      <option value="Helvetica, sans-serif">Helvetica</option>
                      <option value="Times New Roman, serif">Times New Roman</option>
                      <option value="Courier New, monospace">Courier New</option>
                      <option value="Georgia, serif">Georgia</option>
                      <option value="Verdana, sans-serif">Verdana</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Font Size (px)</label>
                    <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
                      <input
                        type="range"
                        min="8"
                        max="240"
                        step="1"
                        :value="getFontSizeNumber(selectedWidget.style?.fontSize, 24)"
                        class="w-full"
                        @input="updateWidgetStyle('fontSize', `${$event.target.value}px`)"
                      />
                      <input
                        type="number"
                        min="8"
                        max="240"
                        :value="getFontSizeNumber(selectedWidget.style?.fontSize, 24)"
                        class="input-base w-20 px-2 py-1 text-sm"
                        @input="updateWidgetStyle('fontSize', `${$event.target.value || 24}px`)"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Color</label>
                    <input
                      v-model="selectedWidget.style.color"
                      type="color"
                      class="w-full h-10 bg-slate-800/50 border border-slate-700 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @input="updateWidgetStyle('color', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Background Color</label>
                    <input
                      :value="getBackgroundHex(selectedWidget.style?.backgroundColor, '#000000')"
                      type="color"
                      class="w-full h-10 bg-slate-800/50 border border-slate-700 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @input="updateWidgetStyle('backgroundColor', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Text Align</label>
                    <select
                      v-model="selectedWidget.style.textAlign"
                      class="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @change="updateWidgetStyle('textAlign', $event.target.value)"
                    >
                      <option value="left">Left</option>
                      <option value="center">Center</option>
                      <option value="right">Right</option>
                      <option value="justify">Justify</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Image/Video Widget Properties -->
              <div v-if="selectedWidget.type === 'image' || selectedWidget.type === 'video'">
                <h3 class="text-sm font-semibold mb-3 text-gray-400 uppercase">{{ selectedWidget.type === 'image' ? 'Image' : 'Video' }} Properties</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Media Source</label>
                    <div class="flex gap-2">
                      <button
                        @click="openMediaLibrary(selectedWidget.type)"
                        class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        Select from Library
                      </button>
                    </div>
                    <div v-if="selectedWidget.content" class="mt-2">
                      <label class="block text-xs font-medium text-gray-400 mb-1.5">Current URL</label>
                      <div class="flex gap-2">
                        <input
                          v-model="selectedWidget.content"
                          type="text"
                          placeholder="Enter image/video URL"
                          class="flex-1 px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                          @input="updateWidgetProperty('content', $event.target.value)"
                        />
                        <button
                          @click="selectedWidget.content = ''; updateWidgetProperty('content', '')"
                          class="px-3 py-2 bg-red-600/50 hover:bg-red-600 text-white rounded-lg text-sm transition-colors duration-200"
                          title="Clear URL"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                      <!-- Preview -->
                      <div v-if="selectedWidget.content" class="mt-2 rounded-lg overflow-hidden border border-slate-700 bg-slate-800/30">
                        <img
                          v-if="selectedWidget.type === 'image'"
                          :src="selectedWidget.content"
                          alt="Preview"
                          class="w-full h-32 object-cover"
                          @error="handlePreviewError"
                        />
                        <video
                          v-else-if="selectedWidget.type === 'video'"
                          :src="selectedWidget.content"
                          class="w-full h-32 object-cover"
                          muted
                          preload="metadata"
                        />
                      </div>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Object Fit</label>
                    <select
                      v-model="selectedWidget.style.objectFit"
                      class="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @change="updateWidgetStyle('objectFit', $event.target.value)"
                    >
                      <option value="contain">Contain</option>
                      <option value="cover">Cover</option>
                      <option value="fill">Fill</option>
                      <option value="none">None</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Clock/Date Widget Properties -->
              <div v-if="selectedWidget.type === 'clock' || selectedWidget.type === 'date'">
                <h3 class="text-sm font-semibold mb-3 text-gray-400 uppercase">{{ selectedWidget.type === 'clock' ? 'Clock' : 'Date' }} Properties</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Format</label>
                    <input
                      v-model="selectedWidget.content"
                      type="text"
                      :placeholder="selectedWidget.type === 'clock' ? 'HH:mm:ss' : 'YYYY-MM-DD'"
                      class="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @input="updateWidgetProperty('content', $event.target.value)"
                    />
                  </div>
                  <div v-if="selectedWidget.type === 'clock'">
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Time Zone</label>
                    <select
                      :value="selectedWidget.style?.timeZone || defaultTimeZone"
                      class="select-base w-full px-3 py-2 text-sm"
                      @change="updateWidgetStyle('timeZone', $event.target.value)"
                    >
                      <option
                        v-for="zone in worldTimeZones"
                        :key="zone.value"
                        :value="zone.value"
                      >
                        {{ zone.label }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Font Size (px)</label>
                    <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
                      <input
                        type="range"
                        min="12"
                        max="220"
                        step="1"
                        :value="getFontSizeNumber(selectedWidget.style?.fontSize, selectedWidget.type === 'clock' ? 56 : 40)"
                        class="w-full"
                        @input="updateWidgetStyle('fontSize', `${$event.target.value}px`)"
                      />
                      <input
                        type="number"
                        min="12"
                        max="220"
                        :value="getFontSizeNumber(selectedWidget.style?.fontSize, selectedWidget.type === 'clock' ? 56 : 40)"
                        class="input-base w-20 px-2 py-1 text-sm"
                        @input="updateWidgetStyle('fontSize', `${$event.target.value || (selectedWidget.type === 'clock' ? 56 : 40)}px`)"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Text Color</label>
                    <input
                      :value="selectedWidget.style?.color || '#ffffff'"
                      type="color"
                      class="w-full h-10 bg-slate-800/50 border border-slate-700 rounded-lg cursor-pointer"
                      @input="updateWidgetStyle('color', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Background Color</label>
                    <input
                      :value="getBackgroundHex(selectedWidget.style?.backgroundColor, '#000000')"
                      type="color"
                      class="w-full h-10 bg-slate-800/50 border border-slate-700 rounded-lg cursor-pointer"
                      @input="updateWidgetStyle('backgroundColor', $event.target.value)"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Font Family</label>
                    <select
                      :value="selectedWidget.style?.fontFamily || 'Arial, sans-serif'"
                      class="select-base w-full px-3 py-2 text-sm"
                      @change="updateWidgetStyle('fontFamily', $event.target.value)"
                    >
                      <option value="Arial, sans-serif">Arial</option>
                      <option value="Helvetica, sans-serif">Helvetica</option>
                      <option value="'Segoe UI', sans-serif">Segoe UI</option>
                      <option value="Roboto, sans-serif">Roboto</option>
                      <option value="Verdana, sans-serif">Verdana</option>
                      <option value="Georgia, serif">Georgia</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Text Align</label>
                    <select
                      :value="selectedWidget.style?.textAlign || 'center'"
                      class="select-base w-full px-3 py-2 text-sm"
                      @change="updateWidgetStyle('textAlign', $event.target.value)"
                    >
                      <option value="left">Left</option>
                      <option value="center">Center</option>
                      <option value="right">Right</option>
                    </select>
                  </div>
                </div>
              </div>

              <div v-if="selectedWidget.type === 'webview'">
                <h3 class="text-sm font-semibold mb-3 text-gray-400 uppercase">Webview Properties</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">URL</label>
                    <input
                      v-model="selectedWidget.content"
                      type="url"
                      placeholder="https://example.com"
                      class="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      @input="updateWidgetProperty('content', $event.target.value)"
                    />
                  </div>
                </div>
              </div>

              <div v-if="selectedWidget.type === 'chart'">
                <ChartEditorPanel
                  :widget="selectedWidget"
                  @update="handleChartWidgetUpdate"
                />
              </div>
            </div>

            <div v-else-if="rightPanelTab === 'properties'" class="text-center py-12">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-700/50 mb-4">
                <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <h3 class="text-sm font-medium text-slate-300 mb-2">No widget selected</h3>
              <p class="text-xs text-slate-400">Select a widget from the canvas to edit its properties</p>
            </div>

            <div v-if="rightPanelTab === 'layers'">
              <h3 class="text-sm font-semibold mb-3 text-gray-400 uppercase tracking-wide">Layers ({{ widgets.length }})</h3>
              <div v-if="widgets.length === 0" class="text-center py-8">
                <svg class="w-12 h-12 mx-auto text-gray-600 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-sm text-gray-400">No widgets yet</p>
                <p class="text-xs text-gray-500 mt-1">Add widgets to get started</p>
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="widget in sortedWidgetsByZIndex"
                  :key="widget.id"
                  :draggable="true"
                  @dragstart="handleDragStart($event, widget.id)"
                  @dragover.prevent="handleDragOver($event)"
                  @drop="handleDrop($event, widget.id)"
                  @dragenter.prevent
                  @click="selectWidget(widget.id)"
                  :class="[
                    'px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 text-sm border',
                    selectedWidgetId === widget.id ? 'bg-accent-color text-white border-accent-color shadow-lg' : 'bg-card hover:bg-card border-border-color text-primary',
                    draggingWidgetId === widget.id ? 'opacity-50' : '',
                    dragOverWidgetId === widget.id ? 'ring-2 ring-blue-400' : ''
                  ]"
                >
                  <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 flex-1 min-w-0">
                      <button
                        @click.stop="toggleWidgetVisibility(widget.id)"
                        :class="[
                          'transition-colors duration-200 flex-shrink-0',
                          widget.visible !== false ? 'text-gray-400 hover:text-gray-300' : 'text-gray-600 opacity-50'
                        ]"
                        :title="widget.visible !== false ? 'Hide Widget' : 'Show Widget'"
                      >
                        <svg v-if="widget.visible !== false" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.29 3.29m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.736m-7.101 2.101l-3.29-3.29" />
                        </svg>
                      </button>
                      <span v-if="editingWidgetId !== widget.id" @dblclick.stop="startEditingWidgetName(widget.id)" class="font-medium truncate cursor-text">{{ widget.name }}</span>
                      <input
                        v-else
                        v-model="editingWidgetName"
                        @blur="finishEditingWidgetName(widget.id)"
                        @keyup.enter="finishEditingWidgetName(widget.id)"
                        @keyup.esc="cancelEditingWidgetName"
                        class="font-medium bg-gray-800 border border-blue-500 rounded px-1 py-0.5 text-sm flex-1 min-w-0"
                        @click.stop
                        ref="widgetNameInput"
                      />
                      <span class="text-xs text-gray-400 flex-shrink-0 ml-auto">Z:{{ widget.zIndex }}</span>
                    </div>
                    <button @click.stop="deleteWidget(widget.id)" class="text-red-400 hover:text-red-300 active:scale-95 transition-all duration-200 flex-shrink-0 ml-2" title="Delete Widget">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                  <div class="text-xs text-gray-400 mt-1.5 flex items-center gap-2">
                    <span class="px-1.5 py-0.5 bg-gray-600/50 rounded text-[10px] uppercase">{{ widget.type }}</span>
                    <span class="text-gray-500">{{ Math.round(widget.width) }}×{{ Math.round(widget.height) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Media Library Modal -->
    <MediaLibraryModal
      :show="showMediaLibrary"
      :filter-by-type="mediaLibraryFilterType"
      :widget-id="selectedWidget?.id"
      @close="showMediaLibrary = false"
      @select="handleMediaSelect"
    />

    <!-- Push to Screen Modal -->
    <PushToScreenModal
      :show="showPushModal"
      :template="currentTemplate"
      :online-screens="onlineScreens"
      :loading="pushing"
      @close="showPushModal = false"
      @select="handlePushToScreenSelect"
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTemplatesStore } from '@/stores/templates'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'
import Moveable from 'vue3-moveable'
import AppLayout from '@/components/layout/AppLayout.vue'
import WidgetPreview from './components/WidgetPreview.vue'
import ChartEditorPanel from './components/chart/ChartEditorPanel.vue'
import MediaLibraryModal from '@/components/common/MediaLibraryModal.vue'
import PushToScreenModal from '@/components/templates/PushToScreenModal.vue'
import { useScreensStore } from '@/stores/screens'

const route = useRoute()
const router = useRouter()
const templatesStore = useTemplatesStore()
const screensStore = useScreensStore()
const notify = useNotification()

// Expose Math for template usage
const Math = window.Math

// Template ID from route params (if editing existing template)
const templateId = computed(() => route.params.id)

// Template state - Initialize from query params if available
const templateName = ref(route.query.name || 'New Template')
const canvasWidth = ref(parseInt(route.query.width) || 1920)
const canvasHeight = ref(parseInt(route.query.height) || 1080)
const canvasBackgroundColor = ref('#ffffff')
const canvasBackgroundImage = ref('')
const targetScreenId = ref(route.query.screen_id || null)
const saving = ref(false)
const loading = ref(false)
const pushing = ref(false)
const showPushModal = ref(false)
const currentTemplate = ref(null)

// Widgets array
const widgets = ref([])

// Selected widget
const selectedWidgetId = ref(null)
const selectedWidget = computed(() => {
  return widgets.value.find(w => w.id === selectedWidgetId.value)
})

// Widget visibility state (default to visible)
const widgetVisibility = ref({})

// Drag and drop state
const draggingWidgetId = ref(null)
const dragOverWidgetId = ref(null)

// Widget name editing state
const editingWidgetId = ref(null)
const editingWidgetName = ref('')
const widgetNameInput = ref(null)

// Media Library Modal state
const showMediaLibrary = ref(false)
const mediaLibraryFilterType = ref(null)
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const rightPanelTab = ref('properties')
const defaultTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
const worldTimeZones = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'Asia/Tehran', label: 'Tehran (Asia/Tehran)' },
  { value: 'Asia/Dubai', label: 'Dubai (Asia/Dubai)' },
  { value: 'Europe/London', label: 'London (Europe/London)' },
  { value: 'Europe/Paris', label: 'Paris (Europe/Paris)' },
  { value: 'Europe/Berlin', label: 'Berlin (Europe/Berlin)' },
  { value: 'America/New_York', label: 'New York (America/New_York)' },
  { value: 'America/Chicago', label: 'Chicago (America/Chicago)' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (America/Los_Angeles)' },
  { value: 'America/Toronto', label: 'Toronto (America/Toronto)' },
  { value: 'America/Sao_Paulo', label: 'Sao Paulo (America/Sao_Paulo)' },
  { value: 'Africa/Johannesburg', label: 'Johannesburg (Africa/Johannesburg)' },
  { value: 'Asia/Kolkata', label: 'India (Asia/Kolkata)' },
  { value: 'Asia/Bangkok', label: 'Bangkok (Asia/Bangkok)' },
  { value: 'Asia/Singapore', label: 'Singapore (Asia/Singapore)' },
  { value: 'Asia/Shanghai', label: 'Shanghai (Asia/Shanghai)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (Asia/Tokyo)' },
  { value: 'Australia/Sydney', label: 'Sydney (Australia/Sydney)' },
]

// Sort widgets by z-index for display
const sortedWidgetsByZIndex = computed(() => {
  return [...widgets.value].sort((a, b) => {
    // First sort by z-index
    if (a.zIndex !== b.zIndex) {
      return a.zIndex - b.zIndex
    }
    // If z-index is same, maintain original order
    return widgets.value.indexOf(a) - widgets.value.indexOf(b)
  })
})

// Canvas scaling
const canvasContainer = ref(null)
const canvasWrapper = ref(null)
const canvasArea = ref(null)
const scale = ref(0.5)

// Moveable references
const moveableRef = ref(null)
const selectedWidgetElement = ref(null)
const widgetRefs = ref({})
const dragStartState = ref(null)
const resizeStartState = ref(null)

// Generate unique ID
const generateId = () => {
  return `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Set widget ref
const setWidgetRef = (el, widgetId) => {
  if (el) {
    widgetRefs.value[widgetId] = el
  }
}

// Get widget elements for snapping
const widgetElements = computed(() => {
  return widgets.value
    .filter(w => w.id !== selectedWidgetId.value)
    .map(w => widgetRefs.value[w.id])
    .filter(Boolean)
})

// Canvas bounds for Moveable (in internal/canvas coordinates)
// Using internal bounds instead of viewport bounds works better with zoom transform
// Moveable with zoom prop can handle internal coordinate bounds
const canvasBounds = computed(() => {
  return {
    left: 0,
    top: 0,
    right: canvasWidth.value,
    bottom: canvasHeight.value
  }
})

// Calculate scale to fit viewport - Auto-scale to fill available space
const calculateScale = () => {
  if (!canvasContainer.value) return

  const container = canvasContainer.value
  // Leave comfortable margin for better UX (20px on each side = 40px total)
  // This ensures the canvas doesn't touch the edges
  const margin = 20
  const containerWidth = container.clientWidth - (margin * 2)
  const containerHeight = container.clientHeight - (margin * 2)

  // Calculate scale to fit both dimensions
  // Canvas width + bezel padding (12px * 2 = 24px)
  const totalCanvasWidth = canvasWidth.value + 24
  const totalCanvasHeight = canvasHeight.value + 24
  
  // Calculate scale for both dimensions to maintain aspect ratio
  const scaleX = containerWidth / totalCanvasWidth
  const scaleY = containerHeight / totalCanvasHeight

  // Use the smaller scale to ensure canvas fits perfectly (contain fit)
  // This maintains aspect ratio and prevents distortion
  scale.value = Math.min(scaleX, scaleY, 1)
}

// Handle wheel for zoom
const handleWheel = (e) => {
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault()
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    scale.value = Math.max(0.1, Math.min(2, scale.value + delta))
  }
}

const zoomIn = () => {
  scale.value = Math.min(2, scale.value + 0.1)
}

const zoomOut = () => {
  scale.value = Math.max(0.1, scale.value - 0.1)
}

// Add widget
const addWidget = (type) => {
  const defaultWidth = type === 'text' ? 300 : type === 'image' || type === 'video' || type === 'webview' ? 400 : type === 'chart' ? 500 : 200
  const defaultHeight = type === 'text' ? 100 : type === 'image' || type === 'video' || type === 'webview' ? 300 : type === 'chart' ? 300 : 100

  const widget = {
    id: generateId(),
    type,
    name: `${type.charAt(0).toUpperCase() + type.slice(1)} Widget ${widgets.value.length + 1}`,
    x: (canvasWidth.value - defaultWidth) / 2,
    y: (canvasHeight.value - defaultHeight) / 2,
    width: defaultWidth,
    height: defaultHeight,
    rotation: 0,
    zIndex: widgets.value.length,
    visible: true, // Default to visible
    content:
      type === 'text'
        ? 'Sample Text'
        : type === 'clock'
        ? 'HH:mm:ss'
        : type === 'date'
        ? 'YYYY-MM-DD'
        : type === 'webview'
        ? 'https://example.com'
        : type === 'chart'
        ? '{"type":"bar","data":{"labels":["A","B","C"],"datasets":[{"label":"Series","data":[12,19,7]}]}}'
        : '',
    style: {
      color: type === 'text' || type === 'clock' || type === 'date' ? '#000000' : undefined,
      fontSize: type === 'text' || type === 'clock' || type === 'date' ? '24px' : undefined,
      fontFamily: type === 'text' || type === 'clock' || type === 'date' ? 'Arial, sans-serif' : undefined,
      textAlign: type === 'text' ? 'left' : undefined,
      backgroundColor: type === 'text' ? 'transparent' : (type === 'clock' || type === 'date' ? '#000000' : undefined),
      timeZone: type === 'clock' ? defaultTimeZone : undefined,
      objectFit: type === 'image' || type === 'video' ? 'cover' : undefined,
    }
  }

  widgets.value.push(widget)
  widgetVisibility.value[widget.id] = true
  selectedWidgetId.value = widget.id

  nextTick(() => {
    updateSelectedWidgetElement()
  })
}

// Select widget
const selectWidget = (widgetId) => {
  selectedWidgetId.value = widgetId
  nextTick(() => {
    updateSelectedWidgetElement()
  })
}

// Update selected widget element reference
const updateSelectedWidgetElement = () => {
  if (selectedWidgetId.value && widgetRefs.value[selectedWidgetId.value]) {
    selectedWidgetElement.value = widgetRefs.value[selectedWidgetId.value]
  } else {
    selectedWidgetElement.value = null
  }
}

// Watch for widget selection changes
watch(selectedWidgetId, () => {
  nextTick(() => {
    updateSelectedWidgetElement()
  })
})

// Watch for canvas area changes to update bounds reactively
watch([canvasArea, scale], () => {
  // Force recomputation of bounds when canvas position/scale changes
  // This ensures Moveable bounds stay in sync with canvas position
  if (moveableRef.value && canvasArea.value) {
    nextTick(() => {
      if (moveableRef.value) {
        moveableRef.value.updateRect()
      }
    })
  }
}, { flush: 'post' })

// Delete widget
const deleteWidget = (widgetId) => {
  const index = widgets.value.findIndex(w => w.id === widgetId)
  if (index > -1) {
    widgets.value.splice(index, 1)
    if (selectedWidgetId.value === widgetId) {
      selectedWidgetId.value = null
    }
  }
}

const deleteSelectedWidget = () => {
  if (!selectedWidgetId.value) return
  deleteWidget(selectedWidgetId.value)
}

// Get widget style for rendering
const getWidgetStyle = (widget) => {
  // Keep sub-pixel precision during move/resize to avoid jitter.
  const x = Number(widget.x || 0)
  const y = Number(widget.y || 0)
  const width = Number(widget.width || 0)
  const height = Number(widget.height || 0)
  const rotation = Math.round(widget.rotation * 100) / 100 // Round to 2 decimal places for rotation
  
  // Check visibility
  const isVisible = widget.visible !== false
  const widgetBg =
    (widget.type === 'text' || widget.type === 'clock' || widget.type === 'date')
      ? (widget.style?.backgroundColor || 'transparent')
      : 'transparent'
  
  return {
    left: `${x}px`,
    top: `${y}px`,
    width: `${width}px`,
    height: `${height}px`,
    transform: `rotate(${rotation}deg)`,
    zIndex: widget.zIndex,
    display: isVisible ? 'block' : 'none',
    opacity: isVisible ? 1 : 0,
    backgroundColor: widgetBg,
    // Enable GPU acceleration to prevent flickering during movement
    willChange: 'transform, top, left',
  }
}

// Toggle widget visibility
const toggleWidgetVisibility = (widgetId) => {
  const widget = widgets.value.find(w => w.id === widgetId)
  if (widget) {
    widget.visible = widget.visible === false ? true : false
  }
}

// Start editing widget name
const startEditingWidgetName = (widgetId) => {
  const widget = widgets.value.find(w => w.id === widgetId)
  if (widget) {
    editingWidgetId.value = widgetId
    editingWidgetName.value = widget.name
    nextTick(() => {
      if (widgetNameInput.value) {
        const input = Array.isArray(widgetNameInput.value) ? widgetNameInput.value[0] : widgetNameInput.value
        if (input) {
          input.focus()
          input.select()
        }
      }
    })
  }
}

// Finish editing widget name
const finishEditingWidgetName = (widgetId) => {
  const widget = widgets.value.find(w => w.id === widgetId)
  if (widget && editingWidgetName.value.trim()) {
    widget.name = editingWidgetName.value.trim()
  }
  editingWidgetId.value = null
  editingWidgetName.value = ''
}

// Cancel editing widget name
const cancelEditingWidgetName = () => {
  editingWidgetId.value = null
  editingWidgetName.value = ''
}

// Open Media Library Modal
const openMediaLibrary = (widgetType) => {
  // Set filter type based on widget type
  mediaLibraryFilterType.value = widgetType === 'image' ? 'image' : widgetType === 'video' ? 'video' : null
  showMediaLibrary.value = true
}

// Handle media selection from library
const handleMediaSelect = async (data) => {
  if (!selectedWidget.value || !data.url) return
  
  // Update widget content with selected URL
  updateWidgetProperty('content', data.url)
  
  // CRITICAL: Store content_id in widget object for saving
  if (data.content && data.content.id) {
    selectedWidget.value.content_id = data.content.id
  }
  
  // Link content to widget if content ID is available and widget has backend ID
  if (data.content && data.content.id && selectedWidget.value.id) {
    try {
      // Check if widget ID is a UUID (backend format)
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
      const isBackendWidget = uuidRegex.test(selectedWidget.value.id)
      
      if (isBackendWidget) {
        // Widget is saved to backend - link content to widget (PATCH: partial update; PUT would omit required fields)
        const { contentsAPI } = await import('@/services/api')
        await contentsAPI.patch(data.content.id, {
          widget: selectedWidget.value.id
        })
        notify.success('Content linked to widget')
      }
    } catch (error) {
      console.error('Failed to link content to widget:', error)
      // Don't show error to user - content URL is already set, linking is optional
    }
  }
}

// Handle preview image error
const handlePreviewError = (event) => {
  // Hide broken image
  event.target.style.display = 'none'
}

// Drag and drop handlers for z-index reordering
const handleDragStart = (event, widgetId) => {
  draggingWidgetId.value = widgetId
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', widgetId)
}

const handleDragOver = (event) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

const handleDrop = (event, targetWidgetId) => {
  event.preventDefault()
  
  if (!draggingWidgetId.value || draggingWidgetId.value === targetWidgetId) {
    dragOverWidgetId.value = null
    draggingWidgetId.value = null
    return
  }
  
  const draggedWidget = widgets.value.find(w => w.id === draggingWidgetId.value)
  const targetWidget = widgets.value.find(w => w.id === targetWidgetId)
  
  if (draggedWidget && targetWidget) {
    // Swap z-index values
    const tempZIndex = draggedWidget.zIndex
    draggedWidget.zIndex = targetWidget.zIndex
    targetWidget.zIndex = tempZIndex
    
    // Re-sort widgets array to maintain order
    widgets.value.sort((a, b) => a.zIndex - b.zIndex)
  }
  
  dragOverWidgetId.value = null
  draggingWidgetId.value = null
}

const handleDragMoveableStart = () => {
  if (!selectedWidget.value) return
  dragStartState.value = {
    x: Number(selectedWidget.value.x || 0),
    y: Number(selectedWidget.value.y || 0),
  }
}

// Handle drag
const handleDrag = ({ beforeTranslate, beforeDelta }) => {
  if (!selectedWidget.value) return

  const start = dragStartState.value || {
    x: Number(selectedWidget.value.x || 0),
    y: Number(selectedWidget.value.y || 0),
  }

  // Prefer absolute translate from drag start to avoid cumulative delta drift.
  const translate = beforeTranslate || beforeDelta || [0, 0]
  const deltaX = translate[0] / scale.value
  const deltaY = translate[1] / scale.value

  let newX = start.x + deltaX
  let newY = start.y + deltaY

  const maxX = canvasWidth.value - selectedWidget.value.width
  const maxY = canvasHeight.value - selectedWidget.value.height
  
  selectedWidget.value.x = Math.max(0, Math.min(maxX, newX))
  selectedWidget.value.y = Math.max(0, Math.min(maxY, newY))
}

const handleDragEnd = () => {
  dragStartState.value = null
}

// Handle resize
const handleResizeStart = () => {
  if (!selectedWidget.value) return
  resizeStartState.value = {
    x: Number(selectedWidget.value.x || 0),
    y: Number(selectedWidget.value.y || 0),
  }
}

const handleResize = (event) => {
  if (!selectedWidget.value || !event.target) return

  const { target, width, height, drag } = event

  // Use Moveable's resolved width/height directly.
  // Dividing by scale can cause sudden jump-to-fit at low zoom levels.
  const newWidth = Math.max(50, Number(width) || 0)
  const newHeight = Math.max(50, Number(height) || 0)
  target.style.width = `${newWidth}px`
  target.style.height = `${newHeight}px`
  selectedWidget.value.width = newWidth
  selectedWidget.value.height = newHeight

  // Position shift while resizing from left/top handles.
  if (drag && drag.beforeTranslate) {
    const start = resizeStartState.value || {
      x: Number(selectedWidget.value.x || 0),
      y: Number(selectedWidget.value.y || 0),
    }
    const dx = drag.beforeTranslate[0]
    const dy = drag.beforeTranslate[1]
    const newX = start.x + dx
    const newY = start.y + dy
    target.style.left = `${newX}px`
    target.style.top = `${newY}px`
    selectedWidget.value.x = newX
    selectedWidget.value.y = newY
  }
}

const handleResizeEnd = () => {
  resizeStartState.value = null
  // Sync Moveable's internal state after resize ends
  nextTick(() => {
    if (moveableRef.value) {
      moveableRef.value.updateRect()
    }
  })
}

// Handle rotate
const handleRotate = ({ target, rotation }) => {
  if (!selectedWidget.value) return
  selectedWidget.value.rotation = rotation
}

const handleRotateEnd = () => {
  // Optional: Save state or trigger update
}

// Update widget property
const updateWidgetProperty = (property, value) => {
  if (!selectedWidget.value) return
  let numValue = ['x', 'y', 'width', 'height', 'rotation', 'zIndex'].includes(property)
    ? Math.round(parseFloat(value) || 0) // Round to integer for clean coordinates
    : value

  // Enforce boundaries for position and size
  if (property === 'x') {
    numValue = Math.max(0, Math.min(canvasWidth.value - selectedWidget.value.width, numValue))
  } else if (property === 'y') {
    numValue = Math.max(0, Math.min(canvasHeight.value - selectedWidget.value.height, numValue))
  } else if (property === 'width') {
    numValue = Math.max(50, Math.min(canvasWidth.value - selectedWidget.value.x, numValue))
  } else if (property === 'height') {
    numValue = Math.max(50, Math.min(canvasHeight.value - selectedWidget.value.y, numValue))
  }

  selectedWidget.value[property] = numValue

  nextTick(() => {
    if (moveableRef.value) {
      moveableRef.value.updateRect()
    }
  })
}

// Update widget style
const updateWidgetStyle = (property, value) => {
  if (!selectedWidget.value) return
  if (!selectedWidget.value.style) {
    selectedWidget.value.style = {}
  }
  selectedWidget.value.style[property] = value
}

const handleChartWidgetUpdate = ({ content, stylePatch }) => {
  if (!selectedWidget.value || selectedWidget.value.type !== 'chart') return
  selectedWidget.value.content = content
  if (!selectedWidget.value.style) {
    selectedWidget.value.style = {}
  }
  selectedWidget.value.style = {
    ...selectedWidget.value.style,
    ...(stylePatch || {}),
  }
}

// Keyboard shortcuts
const handleKeyDown = (e) => {
  const activeElement = document.activeElement
  const isEditingField = activeElement && (
    ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeElement.tagName) ||
    activeElement.isContentEditable
  )
  if (isEditingField || editingWidgetId.value) return

  if (e.key === 'Delete' && selectedWidgetId.value) {
    deleteWidget(selectedWidgetId.value)
  } else if (e.key.startsWith('Arrow') && selectedWidgetId.value) {
    e.preventDefault()
    const step = e.shiftKey ? 10 : 1
    if (e.key === 'ArrowLeft') {
      selectedWidget.value.x = Math.max(0, selectedWidget.value.x - step)
    } else if (e.key === 'ArrowRight') {
      selectedWidget.value.x = Math.min(canvasWidth.value - selectedWidget.value.width, selectedWidget.value.x + step)
    } else if (e.key === 'ArrowUp') {
      selectedWidget.value.y = Math.max(0, selectedWidget.value.y - step)
    } else if (e.key === 'ArrowDown') {
      selectedWidget.value.y = Math.min(canvasHeight.value - selectedWidget.value.height, selectedWidget.value.y + step)
    }
    
    // Round coordinates to integers
    selectedWidget.value.x = Math.round(selectedWidget.value.x)
    selectedWidget.value.y = Math.round(selectedWidget.value.y)
    
    nextTick(() => {
      if (moveableRef.value) {
        moveableRef.value.updateRect()
      }
    })
  }
}

// Convert percentage string to number
const parsePercentage = (value) => {
  if (typeof value === 'string' && value.endsWith('%')) {
    return parseFloat(value) / 100
  }
  return typeof value === 'number' ? value : parseFloat(value) || 0
}

const getFontSizeNumber = (value, fallback = 24) => {
  if (value === undefined || value === null || value === '') return fallback
  if (typeof value === 'number') return value
  const parsed = Number.parseFloat(String(value).replace('px', '').trim())
  return Number.isFinite(parsed) ? parsed : fallback
}

const getBackgroundHex = (value, fallback = '#000000') => {
  if (!value || typeof value !== 'string') return fallback
  const v = value.trim()
  if (v.startsWith('#')) {
    if (v.length === 4) {
      return `#${v[1]}${v[1]}${v[2]}${v[2]}${v[3]}${v[3]}`
    }
    return v.slice(0, 7)
  }
  const rgbaMatch = v.match(/rgba?\(([^)]+)\)/i)
  if (!rgbaMatch) return fallback
  const parts = rgbaMatch[1].split(',').map(p => Number.parseFloat(p.trim()))
  if (parts.length < 3 || parts.some(n => !Number.isFinite(n))) return fallback
  const toHex = (n) => Math.max(0, Math.min(255, Math.round(n))).toString(16).padStart(2, '0')
  return `#${toHex(parts[0])}${toHex(parts[1])}${toHex(parts[2])}`
}


// Load template data from API
const loadTemplateData = async () => {
  if (!templateId.value) return

  loading.value = true
  try {
    // Fetch template
    const template = await templatesStore.fetchTemplate(templateId.value)
    
    // Set template name and dimensions
    templateName.value = template.name || 'Untitled Template'
    canvasWidth.value = template.width || 1920
    canvasHeight.value = template.height || 1080
    
    // Set background if available in config_json
    if (template.config_json) {
      if (template.config_json.backgroundColor) {
        canvasBackgroundColor.value = template.config_json.backgroundColor
      }
      if (template.config_json.backgroundImage) {
        canvasBackgroundImage.value = template.config_json.backgroundImage
      }
    }
    
    // Load widgets from config_json (editor format)
    widgets.value = []
    
    if (template.config_json && template.config_json.widgets && Array.isArray(template.config_json.widgets)) {
      // Load widgets from config_json (editor's native format)
      for (const widget of template.config_json.widgets) {
        // Convert percentage positions to pixel positions for editing
        const x = typeof widget.x === 'string' && widget.x.endsWith('%')
          ? (parsePercentage(widget.x) * canvasWidth.value)
          : (parseFloat(widget.x) || 0)
        
        const y = typeof widget.y === 'string' && widget.y.endsWith('%')
          ? (parsePercentage(widget.y) * canvasHeight.value)
          : (parseFloat(widget.y) || 0)
        
        const width = typeof widget.width === 'string' && widget.width.endsWith('%')
          ? (parsePercentage(widget.width) * canvasWidth.value)
          : (parseFloat(widget.width) || 200)
        
        const height = typeof widget.height === 'string' && widget.height.endsWith('%')
          ? (parsePercentage(widget.height) * canvasHeight.value)
          : (parseFloat(widget.height) || 100)
        
        // Map widget data to editor format
        const editorWidget = {
          id: widget.id || generateId(),
          type: widget.type,
          name: widget.name || `${widget.type} Widget`,
          x: x,
          y: y,
          width: width,
          height: height,
          rotation: widget.rotation || 0,
          zIndex: widget.zIndex || widget.z_index || 0,
          visible: widget.visible !== undefined ? widget.visible : true, // Default to visible
          content: widget.content || '',
          content_id: widget.content_id || null, // Preserve content_id when loading
          style: widget.style || {}
        }
        
        widgets.value.push(editorWidget)
        // Initialize visibility state
        if (editorWidget.visible !== undefined) {
          widgetVisibility.value[editorWidget.id] = editorWidget.visible !== false
        } else {
          widgetVisibility.value[editorWidget.id] = true
        }
      }
    }
    
    // Sort by z-index
    widgets.value.sort((a, b) => a.zIndex - b.zIndex)
    
  } catch (error) {
    console.error('Failed to load template:', error)
    const parsed = error.apiError || normalizeApiError(error)
    notify.error(parsed.userMessage || 'Failed to load template data')
  } finally {
    loading.value = false
  }
}

// Save template - Convert to percentage-based JSON
const saveTemplate = async () => {
  if (!templateName.value || templateName.value.trim() === '') {
    notify.error('Please enter a template name')
    return
  }

  // Check if offline before attempting to save
  if (!isOnline.value) {
    notify.error('Cannot save while offline. Please wait for connection to be restored.')
    return
  }

  saving.value = true
  try {
    // Build template data for API
    const templateData = {
      name: templateName.value.trim(),
      width: canvasWidth.value,
      height: canvasHeight.value,
      config_json: {
        backgroundColor: canvasBackgroundColor.value,
        backgroundImage: canvasBackgroundImage.value || undefined,
        widgets: widgets.value.map(widget => ({
          id: widget.id,
          type: widget.type,
          name: widget.name,
          // Convert pixels to percentages
          x: `${((widget.x / canvasWidth.value) * 100).toFixed(2)}%`,
          y: `${((widget.y / canvasHeight.value) * 100).toFixed(2)}%`,
          width: `${((widget.width / canvasWidth.value) * 100).toFixed(2)}%`,
          height: `${((widget.height / canvasHeight.value) * 100).toFixed(2)}%`,
          rotation: widget.rotation,
          zIndex: widget.zIndex,
          visible: widget.visible !== undefined ? widget.visible : true, // Include visibility state
          content: widget.content || '',
          content_id: widget.content_id || null, // Include content_id if available
          style: widget.style || {}
        }))
      }
    }
    
    // Add description if available from query params
    if (route.query.description) {
      templateData.description = route.query.description
    }
    
    // Add orientation if available
    if (route.query.orientation) {
      templateData.orientation = route.query.orientation
    }

    let savedTemplate
    if (templateId.value) {
      // Update existing template
      savedTemplate = await templatesStore.updateTemplate(templateId.value, templateData)
      notify.success('Template updated successfully')
    } else {
      // Create new template
      savedTemplate = await templatesStore.createTemplate(templateData)
      notify.success('Template created successfully')
      
      // Navigate to edit mode for the new template
      router.replace(`/templates/${savedTemplate.id}/edit`)
    }
    
    // CRITICAL: Reload template data to get backend widget IDs
    // After saving, widgets are synced to database and get backend UUIDs
    // We need to reload to update local widget IDs with backend UUIDs
    if (savedTemplate.id) {
      await loadTemplateData()
    }
    
    return savedTemplate
  } catch (error) {
    console.error('Failed to save template:', error)
    const parsed = error.apiError || normalizeApiError(error)
    const errorMessage = parsed.userMessage || 'Failed to save template'
    notify.error(errorMessage)
    throw error
  } finally {
    saving.value = false
  }
}

// Navigate back to templates list
const goBack = () => {
  router.push('/templates')
}

// Push to Screen functionality
const onlineScreens = computed(() => {
  return screensStore.onlineScreens || screensStore.screens.filter(s => screensStore.getScreenStatus(s) === 'online')
})

const handlePushToScreen = async () => {
  if (!templateId.value) {
    notify.error('Please save the template first before pushing to screen')
    return
  }

  // Fetch screens to ensure we have the latest online status
  try {
    await screensStore.fetchScreens()
    // Load current template data
    const template = await templatesStore.fetchTemplate(templateId.value)
    currentTemplate.value = template
    showPushModal.value = true
  } catch (error) {
    const parsed = error.apiError || normalizeApiError(error)
    notify.error(parsed.userMessage || 'Failed to load screens')
  }
}

// Handle screen selection from push modal
const handlePushToScreenSelect = async (screen) => {
  if (!templateId.value || !currentTemplate.value) return
  
  pushing.value = true
  try {
    // Step 1: Activate template on the screen
    await templatesStore.activateOnScreen(
      templateId.value,
      screen.id,
      true // sync_content
    )
    
    // Step 2: Send RELOAD command to the screen
    const { useCommandsStore } = await import('@/stores/commands')
    const commandsStore = useCommandsStore()
    
    await commandsStore.createCommand({
      screen_id: screen.id,
      type: 'refresh', // This is the RELOAD command
      payload: {},
      priority: 8, // High priority
    })
    
    notify.success(`Template successfully pushed to ${screen.name || screen.device_id}`)
    showPushModal.value = false
    currentTemplate.value = null
    
    // Refresh templates to update screen counts
    await templatesStore.fetchTemplates()
  } catch (error) {
    const parsed = error.apiError || normalizeApiError(error)
    notify.error(parsed.userMessage || 'Failed to push template to screen')
  } finally {
    pushing.value = false
  }
}

// Export JSON
const exportJSON = async () => {
  const savedTemplate = await saveTemplate()
  const blob = new Blob([JSON.stringify(savedTemplate, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${templateName.value || 'template'}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// Lifecycle
// Offline detection
const isOnline = ref(navigator.onLine)
const offlineWarningShown = ref(false)

const handleOnline = () => {
  isOnline.value = true
  offlineWarningShown.value = false
  notify.success('Connection restored. Changes will now be saved.')
}

const handleOffline = () => {
  isOnline.value = false
  if (!offlineWarningShown.value) {
    offlineWarningShown.value = true
    notify.warning('You are offline. Your changes will not be saved until the connection returns.', {
      title: 'Offline Warning',
      duration: 0, // Persistent until connection returns
      persistent: true
    })
  }
}

onMounted(async () => {
  // Add offline/online event listeners
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  
  // Check initial online status
  if (!navigator.onLine) {
    handleOffline()
  }
  // Load template data if editing (must happen first to get canvas dimensions)
  if (templateId.value) {
    await loadTemplateData()
  }
  
  // Calculate scale after DOM is ready and template is loaded
  await nextTick()
  calculateScale()
  
  // Recalculate scale on window resize
  window.addEventListener('resize', calculateScale)
  window.addEventListener('keydown', handleKeyDown)
  
  // Also recalculate when canvas dimensions change
  watch([canvasWidth, canvasHeight], () => {
    nextTick(() => {
      calculateScale()
    })
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateScale)
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style scoped>
.template-editor {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.widget-element {
  user-select: none;
  outline: none;
  transition: box-shadow 0.4s ease;
}

.widget-element:focus {
  outline: none;
}

/* Widget Selection Border - High Contrast for Light Mode */
.widget-selected {
  box-shadow: 0 0 0 2px var(--accent-color);
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

.dark .widget-selected {
  box-shadow: 0 0 0 2px #3b82f6;
  outline: 2px solid #3b82f6;
}

/* Moveable Library Overrides for Light Mode */
:deep(.moveable-control-box) {
  border-color: var(--accent-color) !important;
}

.dark :deep(.moveable-control-box) {
  border-color: #3b82f6 !important;
}

:deep(.moveable-line) {
  background-color: var(--accent-color) !important;
  opacity: 0.6;
}

.dark :deep(.moveable-line) {
  background-color: #3b82f6 !important;
}

:deep(.moveable-control) {
  background-color: var(--accent-color) !important;
  border-color: var(--accent-color) !important;
}

.dark :deep(.moveable-control) {
  background-color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

/* Monitor Frame Styles - Wall-Mounted Display */
.monitor-frame {
  position: relative;
  display: inline-block;
  background-color: #1a1a1a;
  border-radius: 0.5rem;
  box-sizing: border-box;
  /* Subtle inner bevel effect */
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(0, 0, 0, 0.3);
  border-right: 1px solid rgba(0, 0, 0, 0.3);
  /* Deep drop shadow for depth */
  box-shadow: 0 35px 35px rgba(0, 0, 0, 0.5);
}

.power-indicator {
  z-index: 10;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.6), 0 0 12px rgba(74, 222, 128, 0.4);
}

/* Canvas Area with Professional Grid Background - Eye-Care Optimized */
.canvas-area {
  background-color: var(--bg-primary);
  /* Premium light mode grid pattern */
  background-image: 
    linear-gradient(var(--grid-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
  background-size: 50px 50px;
  transition: background-color 0.4s ease, background-image 0.4s ease;
}

.dark .canvas-area {
  background-color: #1e293b;
  /* Dark mode cosmic grid pattern */
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
}

/* Widget soft shadows for light mode */
.canvas-area > * {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.4s ease;
}

.dark .canvas-area > * {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>

