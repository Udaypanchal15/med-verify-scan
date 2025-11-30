import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card";

export function ProfileHoverCard() {
  return (
    <HoverCard>
      <HoverCardTrigger className="cursor-pointer text-blue-600 hover:underline">
        Hover over me
      </HoverCardTrigger>
      <HoverCardContent>
        <div>
          <h4 className="font-semibold">Uday Panchal</h4>
          <p className="text-sm text-muted-foreground">3rd Year CSE Student | Web & Cloud Enthusiast</p>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
}
