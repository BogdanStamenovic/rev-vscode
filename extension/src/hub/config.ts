// Parser for the hardware configuration XML at /sdcard/FIRST/<name>.xml
// (read via adb; there is no HTTP endpoint for it). Uses fast-xml-parser
// rather than a hand-rolled one since the REV config format nests
// attributes and self-closing tags that are easy to get subtly wrong with
// regex, and the dependency is explicitly allowed by ARCHITECTURE.md.
//
// No vscode dependency, so this is unit tested directly under node.
import { XMLParser } from 'fast-xml-parser';

export interface ConfigDevice {
  name: string;
  xmlTag: string;
  port: string;
}

export interface ConfigHub {
  name: string;
  port: string;
  devices: ConfigDevice[];
}

export interface ParsedConfig {
  hubs: ConfigHub[];
}

function toArray<T>(v: T | T[] | undefined): T[] {
  if (v === undefined || v === null) {
    return [];
  }
  return Array.isArray(v) ? v : [v];
}

// Walks the whole parsed document looking for "LynxModule" nodes at any
// depth (a robot can have LynxModules nested under one or more
// LynxUsbDevice portals, or chained). Each LynxModule is one physical hub;
// everything else under it that isn't an attribute is a connected device.
function collectHubs(node: unknown, hubs: ConfigHub[]): void {
  if (node === null || typeof node !== 'object') {
    return;
  }
  for (const [key, value] of Object.entries(node as Record<string, unknown>)) {
    if (key === 'LynxModule') {
      for (const moduleNode of toArray(value)) {
        hubs.push(extractHub(moduleNode as Record<string, unknown>));
      }
    } else if (!key.startsWith('@_')) {
      for (const child of toArray(value)) {
        collectHubs(child, hubs);
      }
    }
  }
}

function extractHub(moduleNode: Record<string, unknown>): ConfigHub {
  const devices: ConfigDevice[] = [];
  for (const [key, value] of Object.entries(moduleNode)) {
    if (key.startsWith('@_') || key === 'LynxModule') {
      continue;
    }
    for (const deviceNode of toArray(value)) {
      if (deviceNode && typeof deviceNode === 'object') {
        const attrs = deviceNode as Record<string, unknown>;
        devices.push({
          name: String(attrs['@_name'] ?? ''),
          xmlTag: key,
          port: String(attrs['@_port'] ?? ''),
        });
      }
    }
  }
  return {
    name: String(moduleNode['@_name'] ?? ''),
    port: String(moduleNode['@_port'] ?? ''),
    devices,
  };
}

export function parseConfigXml(xml: string): ParsedConfig {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '@_' });
  const doc = parser.parse(xml);
  const hubs: ConfigHub[] = [];
  collectHubs(doc, hubs);
  return { hubs };
}
