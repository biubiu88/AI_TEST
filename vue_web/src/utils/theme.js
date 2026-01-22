import { ElMessage } from 'element-plus'

/**
 * 颜色转换函数
 */
export function useChangeColor() {
  // hex 颜色转 rgb 颜色
  const hexToRgb = (str) => {
    let hexs = ''
    let reg = /^\#?[0-9A-Fa-f]{6}$/
    if (!reg.test(str)) {
      ElMessage.warning('输入错误的hex')
      return ''
    }
    str = str.replace('#', '')
    hexs = str.match(/../g)
    for (let i = 0; i < 3; i++) hexs[i] = parseInt(hexs[i], 16)
    return hexs
  }

  // rgb 颜色转 Hex 颜色
  const rgbToHex = (r, g, b) => {
    let reg = /^\d{1,3}$/
    if (!reg.test(r) || !reg.test(g) || !reg.test(b)) {
      ElMessage.warning('输入错误的rgb颜色值')
      return ''
    }
    let hexs = [r.toString(16), g.toString(16), b.toString(16)]
    for (let i = 0; i < 3; i++) if (hexs[i].length == 1) hexs[i] = `0${hexs[i]}`
    return `#${hexs.join('')}`
  }

  // 加深颜色值
  const getDarkColor = (color, level) => {
    let reg = /^\#?[0-9A-Fa-f]{6}$/
    if (!reg.test(color)) {
      ElMessage.warning('输入错误的hex颜色值')
      return ''
    }
    let rgb = hexToRgb(color)
    for (let i = 0; i < 3; i++) rgb[i] = Math.floor(rgb[i] * (1 - level))
    return rgbToHex(rgb[0], rgb[1], rgb[2])
  }

  // 变浅颜色值
  const getLightColor = (color, level) => {
    let reg = /^\#?[0-9A-Fa-f]{6}$/
    if (!reg.test(color)) {
      ElMessage.warning('输入错误的hex颜色值')
      return ''
    }
    let rgb = hexToRgb(color)
    for (let i = 0; i < 3; i++) rgb[i] = Math.floor((255 - rgb[i]) * level + rgb[i])
    return rgbToHex(rgb[0], rgb[1], rgb[2])
  }

  return {
    hexToRgb,
    rgbToHex,
    getDarkColor,
    getLightColor,
  }
}

/**
 * HSL 转 RGB
 */
export const hslToRgb = (h, s, l) => {
  function hue2rgb(p, q, t) {
    if (t < 0) t += 1
    if (t > 1) t -= 1
    if (t < 1 / 6) return p + (q - p) * 6 * t
    if (t < 1 / 2) return q
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6
    return p
  }

  h /= 360
  s /= 100
  l /= 100

  let q = l < 0.5 ? l * (1 + s) : l + s - l * s
  let p = 2 * l - q

  const r = Math.round(hue2rgb(p, q, h + 1 / 3) * 255)
  const g = Math.round(hue2rgb(p, q, h) * 255)
  const b = Math.round(hue2rgb(p, q, h - 1 / 3) * 255)

  return [r, g, b]
}

export const hexToRgb = (str) => {
  let hexs = ''
  let reg = /^\#?[0-9A-Fa-f]{6}$/
  if (!reg.test(str)) {
    ElMessage.warning('输入错误的hex')
    return ''
  }
  str = str.replace('#', '')
  hexs = str.match(/../g)
  for (let i = 0; i < 3; i++) hexs[i] = parseInt(hexs[i], 16)
  return hexs
}

export const rgbToHex = (r, g, b) => {
  let reg = /^\d{1,3}$/
  if (!reg.test(r) || !reg.test(g) || !reg.test(b)) {
    ElMessage.warning('输入错误的rgb颜色值')
    return ''
  }
  let hexs = [r.toString(16), g.toString(16), b.toString(16)]
  for (let i = 0; i < 3; i++) if (hexs[i].length == 1) hexs[i] = `0${hexs[i]}`
  return `#${hexs.join('')}`
}

export const getDarkColor = (color, level) => {
  const hexTColor = getHexColor(color)
  let rgb = hexToRgb(hexTColor)
  for (let i = 0; i < 3; i++) rgb[i] = Math.floor(rgb[i] * (1 - level))
  return rgbToHex(rgb[0], rgb[1], rgb[2])
}

export const getLightColor = (color, level) => {
  const hexTColor = getHexColor(color)
  let rgb = hexToRgb(hexTColor)
  for (let i = 0; i < 3; i++) rgb[i] = Math.floor((255 - rgb[i]) * level + rgb[i])
  return rgbToHex(rgb[0], rgb[1], rgb[2])
}

export const getHexColor = (color) => {
  const hexColorPattern = /^#([0-9A-F]{3}){1,2}$/i
  const rgbColorPattern = /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/
  const hslColorPattern = /^hsl\(\s*(\d{1,3})\s*[\s,]*(\d{1,3})%\s*[\s,]*(\d{1,3})%\s*\)$/
  
  if (hexColorPattern.test(color)) {
    return color
  }
  
  if (rgbColorPattern.test(color)) {
    const matches = color.match(rgbColorPattern)
    if (matches) {
      const r = parseInt(matches[1], 10)
      const g = parseInt(matches[2], 10)
      const b = parseInt(matches[3], 10)
      return useChangeColor().rgbToHex(r, g, b)
    } else {
      ElMessage.warning('输入错误的颜色值')
      throw new Error('输入错误的颜色值')
    }
  }
  
  if (hslColorPattern.test(color)) {
    const matches = color.match(hslColorPattern)
    if (matches) {
      let h = parseInt(matches[1], 10)
      let s = parseInt(matches[2], 10)
      let l = parseInt(matches[3], 10)
      const rbg = hslToRgb(h, s, l)
      return rgbToHex(...rbg)
    } else {
      ElMessage.warning('输入错误的hsl')
      throw new Error('输入错误的hsl')
    }
  }
  
  ElMessage.warning('输入错误的颜色值')
  throw new Error('输入错误的颜色值')
}
