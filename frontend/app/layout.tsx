import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aylık Fon Değişim",
  description: "Türkiye yatırım fonları için KAP kaynaklı aylık portföy değişim analizi",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
