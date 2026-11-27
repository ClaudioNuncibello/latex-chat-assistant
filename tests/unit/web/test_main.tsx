import { waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

afterEach(() => {
  document.body.innerHTML = "";
  vi.resetModules();
});

test("mounts the app into #root", async () => {
  document.body.innerHTML = '<div id="root"></div>';

  await import("../../../web/src/main");

  await waitFor(() => expect(document.querySelector("#root > main")).not.toBeNull());
});

test("fails when #root is missing", async () => {
  await expect(import("../../../web/src/main")).rejects.toThrow("Missing #root element");
});
