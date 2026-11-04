import { describe, expect, test } from "bun:test";
import { toPublicReport } from "./public_report_list";

describe("public report projection", () => {
  test("publishes only a generalized location and public workflow fields", () => {
    const view = toPublicReport({
      report_code: "REP-001",
      category_name: "Road damage",
      status: "IN_PROGRESS",
      submitted_at: "2026-08-18T09:00:00Z",
      address: "Near the market, Bole, Addis Ababa",
    });

    expect(view).toEqual({
      reference: "REP-001",
      category: "Road damage",
      status: "Work in progress",
      submitted_at: "2026-08-18T09:00:00Z",
      general_location: "Bole, Addis Ababa",
    });
    expect(Object.keys(view)).not.toContain("citizen_contact");
    expect(Object.keys(view)).not.toContain("internal_note");
  });

  test("does not invent a location when none is recorded", () => {
    const view = toPublicReport({
      report_code: "REP-002",
      category_name: "Water supply interruption",
      status: "NEW",
      submitted_at: "2026-08-18T09:00:00Z",
      address: "",
    });
    expect(view.general_location).toBeNull();
  });
});
