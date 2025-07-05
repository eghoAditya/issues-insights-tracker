// global.d.ts

interface GoogleAccountsId {
  initialize: (options: { client_id: string; callback: (response: any) => void }) => void;
  prompt: () => void;
}

interface GoogleAccounts {
  id: GoogleAccountsId;
}

interface Google {
  accounts: GoogleAccounts;
}

interface Window {
  google?: Google;
}
