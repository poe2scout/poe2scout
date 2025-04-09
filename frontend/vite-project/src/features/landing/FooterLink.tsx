import { Link as MuiLink, LinkProps } from "@mui/material";

interface FooterLinkProps extends LinkProps {
  href: string;
  children: React.ReactNode;
  external?: boolean;
  disabled?: boolean;
}

export function FooterLink({ href, children, external = false, disabled = false, ...props }: FooterLinkProps) {
  const linkProps = external
    ? { target: "_blank", rel: "noopener noreferrer" }
    : {};

  const disabledStyles = disabled
    ? { pointerEvents: 'none', opacity: 0.6 }
    : {};

  return (
    <MuiLink
      href={!disabled ? href : undefined} 
      color="inherit"
      sx={{
        color: 'grey.400',
        '&:hover': {
          color: !disabled ? 'common.white' : 'grey.400', 
        },
        textDecoration: 'none', 
        ...disabledStyles,
      }}
      {...linkProps}
      {...props}
    >
      {children}
    </MuiLink>
  );
} 