/**
 * Tracks the exact bytes loaded by an Ink view.
 *
 * A clean open/close must not rewrite an older schema or normalize the user's
 * Markdown. The first real edit opts the view into serialization with the
 * current schema. Protected loads always echo their original bytes.
 */
export class InkPersistenceState {
  private originalRaw: string | null = null;
  private protectedLoad = false;
  private dirty = false;

  load(raw: string, protect: boolean): void {
    this.originalRaw = raw;
    this.protectedLoad = protect;
    this.dirty = false;
  }

  reset(): void {
    this.originalRaw = null;
    this.protectedLoad = false;
    this.dirty = false;
  }

  get isProtected(): boolean {
    return this.protectedLoad;
  }

  markDirty(): void {
    if (!this.protectedLoad) this.dirty = true;
  }

  output(buildCurrent: () => string): string {
    if ((!this.dirty || this.protectedLoad) && this.originalRaw !== null) {
      return this.originalRaw;
    }
    return buildCurrent();
  }
}
