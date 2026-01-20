declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_API_URL: string;
      [key: string]: string | undefined;
    }
  }
}

export {};
