/**
 * Script to update all toastStore references to useNotification
 * Run this once to migrate all files
 */

const fs = require('fs')
const path = require('path')
const glob = require('glob')

const files = glob.sync('**/*.{vue,js}', {
  cwd: path.join(__dirname, '..'),
  ignore: ['node_modules/**', 'dist/**', 'build/**']
})

files.forEach(file => {
  const filePath = path.join(__dirname, '..', file)
  let content = fs.readFileSync(filePath, 'utf8')
  let modified = false

  // Replace imports
  if (content.includes("from '@/stores/toast'") || content.includes('from "@/stores/toast"')) {
    content = content.replace(
      /import\s+{\s*useToastStore\s*}\s+from\s+['"]@\/stores\/toast['"]/g,
      "import { useNotification } from '@/composables/useNotification'"
    )
    modified = true
  }

  // Replace store initialization
  if (content.includes('useToastStore()')) {
    content = content.replace(
      /const\s+toastStore\s*=\s*useToastStore\(\)/g,
      'const notify = useNotification()'
    )
    modified = true
  }

  // Replace method calls
  content = content.replace(/toastStore\.success\(/g, 'notify.success(')
  content = content.replace(/toastStore\.error\(/g, 'notify.error(')
  content = content.replace(/toastStore\.warning\(/g, 'notify.warning(')
  content = content.replace(/toastStore\.info\(/g, 'notify.info(')
  content = content.replace(/toastStore\.show\(/g, 'notify.show(')
  content = content.replace(/toastStore\.remove\(/g, 'notify.remove(')
  content = content.replace(/toastStore\.clear\(/g, 'notify.clear(')

  if (modified || content.includes('notify.')) {
    fs.writeFileSync(filePath, content, 'utf8')
    console.log(`Updated: ${file}`)
  }
})

console.log('Migration complete!')

