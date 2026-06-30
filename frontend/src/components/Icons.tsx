import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function IconBase({ children, className = 'h-5 w-5', ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  )
}

export function ActivityIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M3 12h4l3-8 4 16 3-8h4" />
    </IconBase>
  )
}

export function AlertTriangleIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 3 2.5 20h19L12 3Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </IconBase>
  )
}

export function BellIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
      <path d="M10 21h4" />
    </IconBase>
  )
}

export function CheckIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m5 12 4 4L19 6" />
    </IconBase>
  )
}

export function ClockIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </IconBase>
  )
}

export function DroneIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M10 12h4" />
      <path d="M12 10v4" />
      <rect x="9" y="9" width="6" height="6" rx="1.5" />
      <circle cx="4.5" cy="4.5" r="2" />
      <circle cx="19.5" cy="4.5" r="2" />
      <circle cx="4.5" cy="19.5" r="2" />
      <circle cx="19.5" cy="19.5" r="2" />
      <path d="M8 8 6 6" />
      <path d="m16 8 2-2" />
      <path d="m8 16-2 2" />
      <path d="m16 16 2 2" />
    </IconBase>
  )
}

export function FilterIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 6h16" />
      <path d="M7 12h10" />
      <path d="M10 18h4" />
    </IconBase>
  )
}

export function LogOutIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M10 17l5-5-5-5" />
      <path d="M15 12H3" />
      <path d="M21 5v14" />
    </IconBase>
  )
}

export function LockIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="5" y="10" width="14" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </IconBase>
  )
}

export function MapIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Z" />
      <path d="M9 3v15" />
      <path d="M15 6v15" />
    </IconBase>
  )
}

export function PlayIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m8 5 11 7-11 7V5Z" />
    </IconBase>
  )
}

export function ShieldIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 3 5 6v5c0 4.5 2.8 8.3 7 10 4.2-1.7 7-5.5 7-10V6l-7-3Z" />
      <path d="m9.5 12 1.8 1.8 3.7-4" />
    </IconBase>
  )
}

export function UserIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </IconBase>
  )
}

export function VideoIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="3" y="6" width="13" height="12" rx="2" />
      <path d="m16 10 5-3v10l-5-3" />
    </IconBase>
  )
}

export function WifiIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M5 12.5a10 10 0 0 1 14 0" />
      <path d="M8.5 16a5 5 0 0 1 7 0" />
      <path d="M12 20h.01" />
    </IconBase>
  )
}

export function WifiOffIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m3 3 18 18" />
      <path d="M5 12.5a10 10 0 0 1 5.2-2.8" />
      <path d="M14 10a10 10 0 0 1 5 2.5" />
      <path d="M8.5 16a5 5 0 0 1 4.4-1.4" />
      <path d="M12 20h.01" />
    </IconBase>
  )
}

export function XIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </IconBase>
  )
}
