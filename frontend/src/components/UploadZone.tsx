'use client'

import { useState, useRef, useCallback, DragEvent, ChangeEvent } from 'react'

interface Props {
  onUpload: (file: File) => Promise<void>
  isUploading: boolean
  error: string | null
}

function UploadIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="40" height="40" rx="10" fill="#f0f4ff" />
      <path
        d="M20 26V16M20 16l-4 4M20 16l4 4"
        stroke="#2563eb"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M13 28h14"
        stroke="#2563eb"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}

function Spinner() {
  return (
    <svg
      className="animate-spin"
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="16" cy="16" r="12" stroke="#e5e7eb" strokeWidth="3" />
      <path
        d="M16 4a12 12 0 0 1 12 12"
        stroke="#2563eb"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="40" height="40" rx="10" fill="#f0fdf4" />
      <path
        d="M12 20l6 6 10-12"
        stroke="#16a34a"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function UploadZone({ onUpload, isUploading, error }: Props) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [localError, setLocalError] = useState<string | null>(null)
  const [uploadDone, setUploadDone] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateAndSet = useCallback((file: File): boolean => {
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setLocalError('Only PDF files are accepted. Please select a PDF.')
      return false
    }
    setLocalError(null)
    return true
  }, [])

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    async (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragOver(false)

      const file = e.dataTransfer.files?.[0]
      if (!file) return

      if (!validateAndSet(file)) return
      setSelectedFile(file)
    },
    [validateAndSet]
  )

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (!file) return
      if (!validateAndSet(file)) return
      setSelectedFile(file)
    },
    [validateAndSet]
  )

  const handleUploadClick = useCallback(async () => {
    if (!selectedFile) return
    try {
      await onUpload(selectedFile)
      setUploadDone(true)
    } catch {
      // error is handled by parent via `error` prop
    }
  }, [selectedFile, onUpload])

  const handleZoneClick = useCallback(() => {
    if (isUploading) return
    inputRef.current?.click()
  }, [isUploading])

  const displayError = error ?? localError

  // Determine border/bg style
  const zoneClass = [
    'relative flex flex-col items-center justify-center rounded-xl transition-all duration-150 cursor-pointer select-none',
    'min-h-[200px] px-8 py-10',
    isDragOver
      ? 'border-2 border-blue-500 bg-blue-50'
      : displayError
      ? 'border-2 border-red-300 bg-red-50 cursor-default'
      : uploadDone
      ? 'border-2 border-green-300 bg-green-50 cursor-default'
      : 'border-2 border-dashed border-[#e1e4ea] bg-white hover:border-blue-300 hover:bg-blue-50/40',
  ].join(' ')

  return (
    <div>
      <div
        className={zoneClass}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!selectedFile && !isUploading ? handleZoneClick : undefined}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') handleZoneClick()
        }}
        aria-label="Upload capability statement PDF"
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={handleFileChange}
          aria-hidden="true"
        />

        {/* Uploading state */}
        {isUploading && (
          <div className="flex flex-col items-center gap-3 text-center">
            <Spinner />
            <p className="text-sm font-medium text-gray-700">
              Analyzing your capability statement...
            </p>
            <p className="text-xs text-gray-400">This usually takes a few seconds</p>
          </div>
        )}

        {/* Success state */}
        {!isUploading && uploadDone && !displayError && (
          <div className="flex flex-col items-center gap-3 text-center">
            <CheckIcon />
            <p className="text-sm font-semibold text-green-700">Upload complete!</p>
            {selectedFile && (
              <p className="text-xs text-gray-500">{selectedFile.name}</p>
            )}
          </div>
        )}

        {/* Error state */}
        {!isUploading && displayError && (
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 6v5M10 14h.01" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" />
                <circle cx="10" cy="10" r="8" stroke="#dc2626" strokeWidth="1.5" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-red-700">{displayError}</p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                setLocalError(null)
                setSelectedFile(null)
                setUploadDone(false)
                inputRef.current?.click()
              }}
              className="text-xs font-medium text-blue-600 hover:underline mt-1"
            >
              Try again
            </button>
          </div>
        )}

        {/* File selected — ready to upload */}
        {!isUploading && !uploadDone && !displayError && selectedFile && (
          <div className="flex flex-col items-center gap-3 text-center w-full">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="3" y="2" width="14" height="16" rx="2" stroke="#2563eb" strokeWidth="1.5" />
                <path d="M7 7h6M7 10h6M7 13h4" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-800">{selectedFile.name}</p>
              <p className="text-xs text-gray-400 mt-0.5">{formatBytes(selectedFile.size)}</p>
            </div>
            <div className="flex gap-2 mt-1">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                  if (inputRef.current) inputRef.current.value = ''
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Remove
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleUploadClick()
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors"
              >
                Upload
              </button>
            </div>
          </div>
        )}

        {/* Idle state */}
        {!isUploading && !uploadDone && !displayError && !selectedFile && (
          <div className="flex flex-col items-center gap-3 text-center">
            <UploadIcon />
            <div>
              <p className="text-sm font-semibold text-gray-700">
                Drop your Capability Statement PDF here
              </p>
              <p className="text-xs text-gray-400 mt-1">or click to browse</p>
            </div>
            <p className="text-[11px] text-gray-300 mt-1">PDF files only · Max 20 MB</p>
          </div>
        )}
      </div>
    </div>
  )
}
