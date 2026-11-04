import { CIRPQueryProvider } from "@/modules/shared/components/query_provider";
import { TransparencyView } from "@/modules/transparency/components/transparency_view";

export default function TransparencyPage() {
  return (
    <CIRPQueryProvider>
      <TransparencyView />
    </CIRPQueryProvider>
  );
}
