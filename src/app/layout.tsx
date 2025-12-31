import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

// 1. Setup the OSRS font
const runescapeFont = localFont({
  src: "../../public/fonts/runescape_uf.ttf",
  variable: "--font-osrs",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ironman Progression Tracker",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // 2. Add the variable to the html tag
    <html lang="en" className={runescapeFont.variable}>
      <body className="bg-[#0b0a08] text-[#ffde00] antialiased">
        <div className="min-h-screen flex flex-col items-center py-10">
          {children}
        </div>
      </body>
    </html>
  );
}