import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AccessibilityProvider } from "@/components/providers/accessibility-provider";
import { MainNav, SkipLink } from "@/components/nav/MainNav";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FineData - Custom Domain Datasets",
  description: "Generate high-quality, domain-specific datasets from billions of web pages—ready for training specialized AI models, research, and analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AccessibilityProvider>
            <SkipLink />
            <QueryProvider>
              <MainNav />
              <main id="main-content" className="min-h-screen">
                {children}
              </main>
            </QueryProvider>
          </AccessibilityProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
