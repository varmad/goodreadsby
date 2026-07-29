import type { ReactNode } from "react";

export const metadata = {
  title: "goodreadsby",
  description: "Who recommended what, when they said it, and the evidence.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "system-ui, sans-serif",
          maxWidth: "42rem",
          margin: "0 auto",
          padding: "2rem 1rem",
          lineHeight: 1.5,
        }}
      >
        {children}
      </body>
    </html>
  );
}
