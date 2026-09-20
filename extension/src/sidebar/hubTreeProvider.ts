// Tree view for the "Hub" sidebar: connection, device/RC/SDK/OS versions,
// active config, hub list (revHubNamesAndVersions), and the active config's
// devices grouped by hub. Auto-refreshes every 5s while visible; the 5s tick
// only re-fetches rcInfo.json (cheap GET) and re-reads the config XML over
// adb only when the active config name actually changed, or on a manual
// refresh - reading /sdcard over adb on every tick would not be cheap.
import * as vscode from 'vscode';
import { getConnection, invalidateConnection, type HubConnection } from '../hub/connection';
import { fetchRcInfo, type RcInfo } from '../hub/rcinfo';
import { fetchActiveConfigXml, parseActiveConfig } from '../hub/configFetch';
import type { ParsedConfig } from '../hub/config';
import { checkConfigChanges } from '../hub/configWatch';
import { log } from '../output';

type NodeKind = 'status' | 'device' | 'config' | 'group' | 'hub' | 'device-leaf' | 'message';

interface TreeNode {
  id: string;
  kind: NodeKind;
  label: string;
  description?: string;
  tooltip?: string;
  icon?: string;
  children?: TreeNode[];
}

function leaf(id: string, kind: NodeKind, label: string, description?: string, icon?: string, tooltip?: string): TreeNode {
  return { id, kind, label, description, icon, tooltip };
}

function group(id: string, label: string, children: TreeNode[], icon?: string): TreeNode {
  return { id, kind: 'group', label, children, icon };
}

function buildTree(conn: HubConnection, rcInfo: RcInfo, config: ParsedConfig | undefined): TreeNode[] {
  const transportLabel = conn.transport === 'usb' ? 'USB' : conn.transport === 'wifi-direct' ? 'Wi-Fi' : 'Manual';
  const statusDesc = conn.adbSerial ? `${transportLabel} · adb ${conn.adbSerial}` : transportLabel;

  const roots: TreeNode[] = [
    leaf('status', 'status', 'Connected', statusDesc, 'plug'),
    leaf(
      'device',
      'device',
      rcInfo.deviceName ?? 'Control Hub',
      `RC ${rcInfo.rcVersion ?? '?'} · SDK ${rcInfo.sdkVersion ?? '?'}${rcInfo.chOsVersion ? ` · OS ${rcInfo.chOsVersion}` : ''}`,
      'device-desktop'
    ),
    leaf('activeConfig', 'config', 'Active configuration', rcInfo.activeConfigName ?? '(none)', 'settings-gear'),
  ];

  const hubs = rcInfo.revHubNamesAndVersions ?? [];
  roots.push(
    group(
      'hubs',
      `Hubs (${hubs.length})`,
      hubs.map((h, i) =>
        leaf(
          `hub-${i}`,
          'hub',
          h.name ?? `Hub ${i}`,
          [h.moduleAddress !== undefined ? `#${h.moduleAddress}` : undefined, h.firmwareVersion]
            .filter(Boolean)
            .join(' · '),
          'circuit-board'
        )
      ),
      'circuit-board'
    )
  );

  if (!config) {
    roots.push(leaf('devices', 'message', 'Devices', 'config unavailable (no adb)', 'warning'));
  } else {
    const deviceGroups = config.hubs.map((hub, hi) =>
      group(
        `devgroup-${hi}`,
        hub.name || `Hub port ${hub.port}`,
        hub.devices.map((d, di) =>
          leaf(`devgroup-${hi}-dev-${di}`, 'device-leaf', d.name, `${d.xmlTag} · port ${d.port}`, 'plug')
        ),
        'server'
      )
    );
    roots.push(group('devices', 'Devices', deviceGroups, 'list-tree'));
  }

  return roots;
}

function errorRoots(message: string): TreeNode[] {
  return [leaf('status', 'status', 'Disconnected', message, 'debug-disconnect', message)];
}

export class HubTreeProvider implements vscode.TreeDataProvider<TreeNode>, vscode.Disposable {
  private readonly onDidChangeTreeDataEmitter = new vscode.EventEmitter<TreeNode | undefined | void>();
  readonly onDidChangeTreeData = this.onDidChangeTreeDataEmitter.event;

  private roots: TreeNode[] = [leaf('status', 'message', 'Connecting…')];
  private lastConfigName: string | undefined;
  private lastConfig: ParsedConfig | undefined;
  private timer: ReturnType<typeof setInterval> | undefined;
  private refreshInFlight: Promise<void> | undefined;

  getTreeItem(node: TreeNode): vscode.TreeItem {
    const item = new vscode.TreeItem(
      node.label,
      node.children ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None
    );
    item.description = node.description;
    item.tooltip = node.tooltip ?? (node.description ? `${node.label} — ${node.description}` : node.label);
    if (node.icon) {
      item.iconPath = new vscode.ThemeIcon(node.icon);
    }
    item.id = node.id;
    return item;
  }

  getChildren(node?: TreeNode): TreeNode[] {
    if (!node) {
      return this.roots;
    }
    return node.children ?? [];
  }

  async refresh(forceConfigReload = false): Promise<void> {
    // Coalesce overlapping refreshes (manual click landing mid-tick).
    if (this.refreshInFlight) {
      return this.refreshInFlight;
    }
    this.refreshInFlight = this.doRefresh(forceConfigReload).finally(() => {
      this.refreshInFlight = undefined;
    });
    return this.refreshInFlight;
  }

  private async doRefresh(forceConfigReload: boolean): Promise<void> {
    try {
      const conn = await getConnection();
      const rcInfo = await fetchRcInfo();

      if (forceConfigReload || rcInfo.activeConfigName !== this.lastConfigName) {
        try {
          const { xml } = await fetchActiveConfigXml(conn, rcInfo.activeConfigName);
          this.lastConfig = parseActiveConfig(xml);
          this.lastConfigName = rcInfo.activeConfigName;
        } catch (err) {
          log(`hub view: could not read active config xml: ${(err as Error).message}`);
          this.lastConfig = undefined;
        }
      }

      this.roots = buildTree(conn, rcInfo, this.lastConfig);
      // Fire-and-forget: this is "on hub connect" / "on sidebar refresh" for
      // configWatch.ts (see its header comment). It does its own adb/hub
      // round trip, so it must not delay the tree's own 5s refresh cycle.
      void checkConfigChanges();
    } catch (err) {
      invalidateConnection();
      this.roots = errorRoots((err as Error).message);
    }
    this.onDidChangeTreeDataEmitter.fire();
  }

  startAutoRefresh(): void {
    if (this.timer) {
      return;
    }
    this.timer = setInterval(() => {
      void this.refresh(false);
    }, 5000);
  }

  stopAutoRefresh(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  dispose(): void {
    this.stopAutoRefresh();
    this.onDidChangeTreeDataEmitter.dispose();
  }
}
